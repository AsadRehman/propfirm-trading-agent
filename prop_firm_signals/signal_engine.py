"""
Mock Capital Phase 1 — Signal Engine
Assets: BTC, ETH, BCH, Gold, Silver, Crude Oil
Indicators: Williams Alligator + Heiken Ashi + RSI + Volume + EMA 50/200
Runs every 5 minutes via GitHub Actions
- Pushes LONG/SHORT signals to ClickUp
- Saves signal history for deduplication and outcome tracking
- Auto-checks pending signals for TP/SL hits
"""

import os
import sys
import json
import time
import threading
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv

RUN_ONCE = "--once" in sys.argv  # set by GitHub Actions; local runs loop forever

sys.stdout.reconfigure(line_buffering=True)

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# --- Config ---
UTC_FMT           = "%Y-%m-%d %H:%M UTC"
EMAIL_SENDER      = os.environ["EMAIL_SENDER"]
EMAIL_APP_PASSWORD= os.environ["EMAIL_APP_PASSWORD"]
EMAIL_RECIPIENT   = os.environ["EMAIL_RECIPIENT"]
HISTORY_FILE      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signal_history.json")

ASSETS = [
    {"name": "BTC",    "symbol": "BTCUSDT", "source": "bybit"},
    {"name": "ETH",    "symbol": "ETHUSDT", "source": "bybit"},
    {"name": "BCH",    "symbol": "BCHUSDT", "source": "bybit"},
    {"name": "GOLD",   "symbol": "GC=F",    "source": "yfinance"},
    {"name": "SILVER", "symbol": "SI=F",    "source": "yfinance"},
    {"name": "OIL",    "symbol": "CL=F",    "source": "yfinance"},
]

BYBIT_INTERVAL   = {"15min": "15", "4h": "240"}  # Bybit uses minutes as integers
YF_INTERVAL      = {"15min": "15m", "4h": "1h"}
YF_PERIOD        = {"15min": "5d",  "4h": "60d"}
CACHE_TTL      = 240  # seconds — reuse commodity data for 4 min
YF_RETRY_DELAY = 5    # seconds between Yahoo retries
YF_MAX_RETRIES = 3
CRUMB_TTL      = 3600 # refresh Yahoo crumb once per hour

_yf_cache:    dict  = {}
_yf_crumb:    str   = ""
_yf_crumb_ts: float = 0.0

_yf_session = requests.Session()
_yf_session.headers.update({
    "User-Agent":      ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"),
    "Accept":          "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin":          "https://finance.yahoo.com",
    "Referer":         "https://finance.yahoo.com/",
})

# INDICATORS

def calc_smma(data, period):
    if len(data) < period:
        return []
    result = [sum(data[:period]) / period]
    for i in range(period, len(data)):
        result.append((result[-1] * (period - 1) + data[i]) / period)
    return result

def calc_alligator(closes):
    return calc_smma(closes, 13), calc_smma(closes, 8), calc_smma(closes, 5)

def calc_heiken_ashi(candles):
    ha = []
    for i, c in enumerate(candles):
        hc = (c["open"] + c["high"] + c["low"] + c["close"]) / 4
        ho = (ha[i-1]["open"] + ha[i-1]["close"]) / 2 if i > 0 else (c["open"] + c["close"]) / 2
        ha.append({"open": ho, "high": max(c["high"], ho, hc),
                   "low": min(c["low"], ho, hc), "close": hc})
    return ha

def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    g = l = 0
    for i in range(1, period + 1):
        d = closes[i] - closes[i-1]
        if d >= 0: g += d
        else:      l -= d
    ag, al = g / period, l / period
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i-1]
        ag = (ag * (period-1) + max(d, 0))  / period
        al = (al * (period-1) + max(-d, 0)) / period
    return 100.0 if al == 0 else 100 - 100 / (1 + ag / al)

def calc_ema(closes, period):
    if len(closes) < period:
        return []
    k = 2 / (period + 1)
    r = [sum(closes[:period]) / period]
    for i in range(period, len(closes)):
        r.append(closes[i] * k + r[-1] * (1 - k))
    return r

def volume_above_avg(volumes):
    if len(volumes) < 20:
        return False
    return volumes[-1] > sum(volumes[-20:]) / 20

# DATA FETCH

def _fetch_bybit(symbol, interval, limit=220):
    url    = "https://api.bybit.com/v5/market/kline"
    params = {"category": "spot", "symbol": symbol,
              "interval": BYBIT_INTERVAL[interval], "limit": limit}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("retCode") != 0:
            print(f"  ⚠ Bybit error {symbol}: {data.get('retMsg')}")
            return None
        # Bybit returns newest-first — reverse to oldest-first
        candles = list(reversed(data["result"]["list"]))
        return [{"open":   float(k[1]), "high": float(k[2]),
                 "low":    float(k[3]), "close": float(k[4]),
                 "volume": float(k[5])} for k in candles]
    except Exception as e:
        print(f"  ⚠ Bybit error {symbol}: {e}")
        return None

def _refresh_yf_crumb():
    global _yf_crumb, _yf_crumb_ts
    now = time.time()
    if _yf_crumb and now - _yf_crumb_ts < CRUMB_TTL:
        return
    try:
        _yf_session.get("https://fc.yahoo.com/", timeout=10)
        resp = _yf_session.get(
            "https://query2.finance.yahoo.com/v1/test/getcrumb", timeout=10)
        if resp.status_code == 200 and resp.text.strip():
            _yf_crumb    = resp.text.strip()
            _yf_crumb_ts = now
            print("  🔑 Yahoo crumb refreshed")
        else:
            print(f"  ⚠ Crumb fetch returned {resp.status_code}")
    except Exception as e:
        print(f"  ⚠ Crumb refresh failed: {e}")

def _yahoo_candles(symbol, yf_interval, yf_range, output_size):
    _refresh_yf_crumb()
    url    = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"interval": yf_interval, "range": yf_range, "events": "history"}
    if _yf_crumb:
        params["crumb"] = _yf_crumb
    resp   = _yf_session.get(url, params=params, timeout=15)
    resp.raise_for_status()
    result = resp.json().get("chart", {}).get("result") or []
    if not result:
        return None
    chart  = result[0]
    quotes = chart["indicators"]["quote"][0]
    data   = []
    for i in range(len(chart["timestamp"])):
        o, h, l, c = quotes["open"][i], quotes["high"][i], quotes["low"][i], quotes["close"][i]
        if None in (o, h, l, c):
            continue
        v = quotes["volume"][i]
        data.append({"open": float(o), "high": float(h), "low": float(l),
                     "close": float(c), "volume": float(v) if v else 1000.0})
    return data[-output_size:] if data else None

def _fetch_yfinance(symbol, interval, output_size=220):
    key = f"{symbol}_{interval}"
    now = time.time()
    if key in _yf_cache and now - _yf_cache[key]["ts"] < CACHE_TTL:
        print(f"  ↩ Using cached data for {symbol} {interval}")
        return _yf_cache[key]["data"]
    last_err = None
    for attempt in range(1, YF_MAX_RETRIES + 1):
        try:
            data = _yahoo_candles(symbol, YF_INTERVAL[interval], YF_PERIOD[interval], output_size)
            if not data:
                print(f"  ⚠ No data returned for {symbol} {interval}")
                return None
            _yf_cache[key] = {"ts": time.time(), "data": data}
            return data
        except Exception as e:
            last_err = e
            print(f"  ⚠ Yahoo error {symbol} (attempt {attempt}/{YF_MAX_RETRIES}): {e}")
            if attempt < YF_MAX_RETRIES:
                time.sleep(YF_RETRY_DELAY)
    if key in _yf_cache:
        print(f"  ↩ Using stale cache for {symbol} {interval}")
        return _yf_cache[key]["data"]
    print(f"  ✖ Giving up on {symbol}: {last_err}")
    return None

def fetch_candles(symbol, interval, source="bybit", output_size=220):
    if source == "bybit":
        return _fetch_bybit(symbol, interval, output_size)
    return _fetch_yfinance(symbol, interval, output_size)

# SIGNAL ANALYSIS HELPERS

def _ha_flags(c15):
    h3    = calc_heiken_ashi(c15)[-3:]
    hbull = all(c["close"] > c["open"] for c in h3)
    hbear = all(c["close"] < c["open"] for c in h3)
    hlw   = any((c["open"] - c["low"]) > (c["high"] - c["close"]) * 0.5 for c in h3)
    huw   = any((c["high"] - c["close"]) > (c["open"] - c["low"]) * 0.5 for c in h3)
    return hbull, hbear, hlw, huw

def _alligator_flags(cl15, cl4h, price):
    j15, t15, l15 = calc_alligator(cl15)
    j4h, t4h, l4h = calc_alligator(cl4h)
    jl, tl, ll    = j15[-1], t15[-1], l15[-1]
    j4, t4, l4    = j4h[-1], t4h[-1], l4h[-1]
    sleeping = abs(ll - jl) / jl < 0.001
    return {
        "sleeping": sleeping,
        "bull15": ll > tl > jl,  "bear15": ll < tl < jl,
        "bull4h": l4 > t4 > j4,  "bear4h": l4 < t4 < j4,
        "pabove": price > ll and price > tl and price > jl,
        "pbelow": price < ll and price < tl and price < jl,
        "sep15":  abs(ll - jl) / jl,
        "sep4h":  abs(l4 - j4) / j4,
    }

def _calc_conviction(direction, sep15, sep4h, score, rsi):
    # Prime RSI zones: LONG momentum builds 50-65, SHORT momentum builds 35-50
    prime_rsi = (50 <= rsi <= 65) if direction == "LONG" else (35 <= rsi <= 50)
    if sep15 > 0.002 and sep4h > 0.002 and score >= 6 and prime_rsi:
        return "HC"
    if sep15 > 0.001 and score >= 5:
        return "MC"
    return "LC"

def _build_signal(direction, conviction, price, rsi, vol_ab):
    rr  = {"HC": 2.0, "MC": 1.5, "LC": 1.0}[conviction]
    tpd = {"HC": 25,  "MC": 20,  "LC": 15 }[conviction]
    sld = round(tpd / rr, 2)
    pct = tpd / 1000
    tpp = price * (1 + pct)        if direction == "LONG" else price * (1 - pct)
    slp = price * (1 - sld / 1000) if direction == "LONG" else price * (1 + sld / 1000)
    return {"direction": direction, "conviction": conviction,
            "price": round(price, 4), "tp_price": round(tpp, 4),
            "sl_price": round(slp, 4), "tp_dollar": tpd,
            "sl_dollar": sld, "rr": rr,
            "rsi": round(rsi, 2), "vol_above": vol_ab}

def _no_trade(al, ema_bull, ema_bear, rsi):
    # Alligator sleeping = market consolidating, no directional edge
    if al["sleeping"] or (not ema_bull and not ema_bear):
        return True
    # Only block at extreme RSI — normal oversold/overbought is fine in trending markets
    if ema_bull and rsi > 80:   # don't long when already extreme overbought
        return True
    if ema_bear and rsi < 20:   # don't short when already extreme oversold (bounce risk)
        return True
    return False

def _score_signals(al, ema_bull, ema_bear, hbull, hbear, hlw, huw, rsi, vol_ab):
    # --- LONG: 3 mandatory + 4 confirming (need total >= 5) ---
    # Mandatory: EMA bullish trend + 4H alligator bullish + price above all alligator lines
    # Confirming: 15min alligator + clean HA bullish + RSI above midline + volume
    ls = sum([
        ema_bull,                            # macro trend: price above EMA 50 & 200
        al["bull4h"],                        # 4H alligator: Jaw < Teeth < Lips (bullish order)
        al["pabove"],                        # price fully above all alligator lines
        al["bull15"] and not al["sleeping"], # 15min alligator confirms direction
        hbull and not hlw,                   # Heiken Ashi bullish, no long lower wick
        40 < rsi < 75,                       # RSI in bullish momentum zone
        vol_ab,                              # volume above 20-bar average
    ])
    # --- SHORT: 3 mandatory + 4 confirming (need total >= 5) ---
    # Mandatory: EMA bearish trend + 4H alligator bearish + price below all alligator lines
    # Confirming: 15min alligator + clean HA bearish + RSI below midline + volume
    ss = sum([
        ema_bear,                            # macro trend: price below EMA 50 & 200
        al["bear4h"],                        # 4H alligator: Jaw > Teeth > Lips (bearish order)
        al["pbelow"],                        # price fully below all alligator lines
        al["bear15"] and not al["sleeping"], # 15min alligator confirms direction
        hbear and not huw,                   # Heiken Ashi bearish, no long upper wick
        rsi < 55,                            # RSI below midline (bearish momentum)
        vol_ab,                              # volume above 20-bar average
    ])
    return ls, ss

def _candles_ok(c15, c4h):
    return c15 and len(c15) >= 50 and c4h and len(c4h) >= 210

def _pick_direction(long_valid, short_valid, ls, ss):
    if long_valid and short_valid:
        return "LONG" if ls >= ss else "SHORT"
    return "LONG" if long_valid else "SHORT"

def _resolve_direction(long_valid, short_valid, ls, ss):
    if not long_valid and not short_valid:
        return None
    return _pick_direction(long_valid, short_valid, ls, ss)

# SIGNAL ANALYSIS

def analyze_signal(c15, c4h):
    if not _candles_ok(c15, c4h):
        return None

    cl15  = [c["close"] for c in c15]
    cl4h  = [c["close"] for c in c4h]
    price = cl15[-1]

    rsi = calc_rsi(cl15)
    if rsi is None:
        return None

    e50  = calc_ema(cl4h, 50)
    e200 = calc_ema(cl4h, 200)
    if not e50 or not e200:
        return None

    vol_ab   = volume_above_avg([c["volume"] for c in c15])
    ema_bull = price > e50[-1] and price > e200[-1]
    ema_bear = price < e50[-1] and price < e200[-1]
    al       = _alligator_flags(cl15, cl4h, price)
    hbull, hbear, hlw, huw = _ha_flags(c15)
    base     = {"price": round(price, 4), "rsi": round(rsi, 2), "vol_above": vol_ab}

    if _no_trade(al, ema_bull, ema_bear, rsi):
        return {**base, "direction": "NO TRADE"}

    ls, ss      = _score_signals(al, ema_bull, ema_bear, hbull, hbear, hlw, huw, rsi, vol_ab)
    long_valid  = ema_bull and al["bull4h"] and al["pabove"] and ls >= 5
    short_valid = ema_bear and al["bear4h"] and al["pbelow"] and ss >= 5
    direction   = _resolve_direction(long_valid, short_valid, ls, ss)

    if direction is None:
        return {**base, "direction": "WATCHING"}

    score      = ls if direction == "LONG" else ss
    conviction = _calc_conviction(direction, al["sep15"], al["sep4h"], score, rsi)
    return _build_signal(direction, conviction, price, rsi, vol_ab)

# OUTCOME CHECKER

def _check_candle(record, candle, tp, sl, now_utc):
    direction = record["direction"]
    asset     = record["asset"]
    if direction == "LONG":
        if candle["high"] >= tp:
            record.update({"outcome": "TP", "outcome_time": now_utc, "outcome_price": tp})
            print(f"  🎯 TP HIT: {asset} LONG @ {tp}")
            return True
        if candle["low"] <= sl:
            record.update({"outcome": "SL", "outcome_time": now_utc, "outcome_price": sl})
            print(f"  ❌ SL HIT: {asset} LONG @ {sl}")
            return True
    elif direction == "SHORT":
        if candle["low"] <= tp:
            record.update({"outcome": "TP", "outcome_time": now_utc, "outcome_price": tp})
            print(f"  🎯 TP HIT: {asset} SHORT @ {tp}")
            return True
        if candle["high"] >= sl:
            record.update({"outcome": "SL", "outcome_time": now_utc, "outcome_price": sl})
            print(f"  ❌ SL HIT: {asset} SHORT @ {sl}")
            return True
    return False

def check_pending_outcomes(history, candles_map):
    now_utc = datetime.now(timezone.utc).strftime(UTC_FMT)
    for record in history:
        if record["outcome"] != "PENDING":
            continue
        candles = candles_map.get(record["asset"])
        if not candles:
            continue
        tp = record["tp_price"]
        sl = record["sl_price"]
        for c in candles[-50:]:
            if _check_candle(record, c, tp, sl, now_utc):
                break
    return history

# HISTORY

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def record_signal(history, asset_name, signal):
    now_utc   = datetime.now(timezone.utc).strftime(UTC_FMT)
    signal_id = f"{asset_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
    hour_prefix = f"{asset_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H')}"
    for r in history[:12]:
        if r["id"].startswith(hour_prefix):
            print(f"  ⏭ Duplicate skipped for {asset_name}")
            return history
    history.insert(0, {
        "id": signal_id, "asset": asset_name,
        "direction": signal["direction"], "conviction": signal.get("conviction", "—"),
        "price": signal["price"], "tp_price": signal.get("tp_price"),
        "sl_price": signal.get("sl_price"), "tp_dollar": signal.get("tp_dollar"),
        "sl_dollar": signal.get("sl_dollar"), "rr": signal.get("rr"),
        "rsi": signal.get("rsi"), "vol_above": signal.get("vol_above"),
        "signal_time": now_utc, "outcome": "PENDING",
        "outcome_time": None, "outcome_price": None,
    })
    return history

# EMAIL ALERT

def send_email_alert(asset_name, signal):
    now_utc = datetime.now(timezone.utc).strftime(UTC_FMT)
    vol     = "Above Average" if signal["vol_above"] else "Below Average"
    subject = f"🔔 {asset_name} — {signal['direction']} ({signal.get('conviction', '—')})"
    body = (
        f"TRADING SIGNAL ALERT\n"
        f"{'='*40}\n"
        f"Asset      : {asset_name}\n"
        f"Direction  : {signal['direction']}\n"
        f"Conviction : {signal.get('conviction', '—')}\n"
        f"Entry Price: {signal['price']}\n"
        f"TP         : {signal['tp_price']}  (+${signal['tp_dollar']})\n"
        f"SL         : {signal['sl_price']}  (-${signal['sl_dollar']})\n"
        f"R:R        : 1:{signal['rr']}\n"
        f"RSI        : {signal['rsi']}\n"
        f"Volume     : {vol}\n"
        f"Time (UTC) : {now_utc}\n"
        f"{'='*40}\n"
    )
    msg = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
            smtp.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print(f"  ✅ Email alert sent to {EMAIL_RECIPIENT}")
    except Exception as e:
        print(f"  ❌ Email error: {e}")

# MAIN

def _print_alert(name, sig):
    now_utc = datetime.now(timezone.utc).strftime(UTC_FMT)
    print("\n" + "!"*55, flush=True)
    print(f"  🚨 ALERT GENERATED — {now_utc}", flush=True)
    print(f"  Asset     : {name}", flush=True)
    print(f"  Direction : {sig['direction']}", flush=True)
    print(f"  Conviction: {sig['conviction']}", flush=True)
    print(f"  Price     : {sig['price']}", flush=True)
    print(f"  TP        : {sig['tp_price']}  (+${sig['tp_dollar']})", flush=True)
    print(f"  SL        : {sig['sl_price']}  (-${sig['sl_dollar']})", flush=True)
    print(f"  RR        : 1:{sig['rr']}", flush=True)
    print(f"  RSI       : {sig['rsi']}", flush=True)
    print(f"  Volume    : {'Above Average' if sig['vol_above'] else 'Below Average'}", flush=True)
    print("!"*55 + "\n", flush=True)

def _heartbeat(stop_event, interval=30):
    start = time.time()
    while not stop_event.wait(interval):
        elapsed = int(time.time() - start)
        print(f"  ⏱ {elapsed}s elapsed — still running...", flush=True)

SCAN_INTERVAL = 5 * 60  # 5 minutes

def _run_once():
    now = datetime.now(timezone.utc).strftime(UTC_FMT)
    print(f"\n{'='*55}\nSignal Engine — {now}\n{'='*55}")

    stop = threading.Event()
    threading.Thread(target=_heartbeat, args=(stop,), daemon=True).start()

    history      = load_history()
    candles_map  = {}
    alerts_fired = 0

    for asset in ASSETS:
        name, symbol, source = asset["name"], asset["symbol"], asset["source"]
        print(f"\n▶ {name}")
        c15 = fetch_candles(symbol, "15min", source)
        c4h = fetch_candles(symbol, "4h",    source)
        if not c15 or not c4h:
            print(f"  ⚠ Skipping {name}")
            continue
        candles_map[name] = c15
        sig = analyze_signal(c15, c4h)
        if not sig:
            print("  — Insufficient data")
            continue
        vol = "▲" if sig["vol_above"] else "▼"
        print(f"  {sig['direction']} | Price:{sig['price']} | RSI:{sig['rsi']} | Vol:{vol}")
        if sig["direction"] in ("LONG", "SHORT"):
            _print_alert(name, sig)
            alerts_fired += 1
            history = record_signal(history, name, sig)
            send_email_alert(name, sig)
        else:
            print(f"  → {sig['direction']}")

    print(f"\n{'─'*55}\nChecking pending outcomes...")
    history = check_pending_outcomes(history, candles_map)
    save_history(history)
    stop.set()

    print("\n" + "="*55)
    if alerts_fired:
        print(f"  ✅ {alerts_fired} alert(s) generated and pushed to ClickUp.")
    else:
        print("  💤 No signals found this run.")
    print(f"  ⏳ Next scan in {SCAN_INTERVAL // 60} minutes.")
    print("="*55 + "\n")

def main():
    if RUN_ONCE:
        print("🚀 Signal Engine — single run mode (GitHub Actions).")
        _run_once()
        return
    print("🚀 Signal Engine started. Press Ctrl+C to stop.")
    while True:
        try:
            _run_once()
        except Exception as e:
            print(f"\n⚠ Run failed: {e} — retrying next cycle.", flush=True)
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
