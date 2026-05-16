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
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# --- Config ---
UTC_FMT         = "%Y-%m-%d %H:%M UTC"
TWELVE_DATA_KEY = os.environ["TWELVE_DATA_API_KEY"]
CLICKUP_API_KEY = os.environ["CLICKUP_API_KEY"]
CLICKUP_LIST_ID = os.environ["CLICKUP_LIST_ID"]
HISTORY_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signal_history.json")

ASSETS = [
    {"name": "BTC",    "symbol": "BTC/USD"},
    {"name": "ETH",    "symbol": "ETH/USD"},
    {"name": "BCH",    "symbol": "BCH/USD"},
    {"name": "GOLD",   "symbol": "XAU/USD"},
    {"name": "SILVER", "symbol": "XAG/USD"},
    {"name": "OIL",    "symbol": "WTI/USD"},
]

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

def fetch_candles(symbol, interval, output_size=220):
    url = (f"https://api.twelvedata.com/time_series"
           f"?symbol={symbol}&interval={interval}"
           f"&outputsize={output_size}&apikey={TWELVE_DATA_KEY}")
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        if "values" not in data:
            print(f"  ⚠ {symbol} {interval}: {data.get('message','no data')}")
            return None
        return [{"open": float(v["open"]), "high": float(v["high"]),
                 "low": float(v["low"]),   "close": float(v["close"]),
                 "volume": float(v.get("volume", 1000))}
                for v in reversed(data["values"])]
    except Exception as e:
        print(f"  ⚠ Fetch error {symbol}: {e}")
        return None

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

def _calc_conviction(direction, sep15, sep4h, cha, rsi):
    rsis = (55 <= rsi <= 65) if direction == "LONG" else (35 <= rsi <= 45)
    if sep15 > 0.002 and sep4h > 0.002 and cha and rsis:
        return "HC"
    if sep15 > 0.001 and cha:
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
    return al["sleeping"] or (not ema_bull and not ema_bear) or rsi >= 70 or rsi <= 30

def _score_signals(al, ema_bull, ema_bear, hbull, hbear, hlw, huw, rsi, vol_ab):
    ls = sum([ema_bull, al["bull4h"], al["bull15"] and not al["sleeping"],
              al["pabove"], hbull and not hlw, 50 < rsi < 70, vol_ab])
    ss = sum([ema_bear, al["bear4h"], al["bear15"] and not al["sleeping"],
              al["pbelow"], hbear and not huw, 30 < rsi < 50, vol_ab])
    return ls, ss

def _cha_flag(direction, hbull, hbear, hlw, huw):
    if direction == "LONG":
        return hbull and not hlw
    return hbear and not huw

# SIGNAL ANALYSIS

def analyze_signal(c15, c4h):
    if not c15 or len(c15) < 50 or not c4h or len(c4h) < 210:
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

    ls, ss = _score_signals(al, ema_bull, ema_bear, hbull, hbear, hlw, huw, rsi, vol_ab)

    if ls < 7 and ss < 7:
        return {**base, "direction": "WATCHING"}

    direction  = "LONG" if ls == 7 else "SHORT"
    cha        = _cha_flag(direction, hbull, hbear, hlw, huw)
    conviction = _calc_conviction(direction, al["sep15"], al["sep4h"], cha, rsi)
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

# CLICKUP

def push_to_clickup(asset_name, signal):
    now_utc = datetime.now(timezone.utc).strftime(UTC_FMT)
    vol     = "Above Average" if signal["vol_above"] else "Below Average"
    desc = (f"Asset: {asset_name}\n"
            f"Direction: {signal['direction']}\n"
            f"Conviction: {signal.get('conviction', '—')}\n"
            f"Entry Price: {signal['price']}\n"
            f"TP: {signal['tp_price']} (+${signal['tp_dollar']})\n"
            f"SL: {signal['sl_price']} (-${signal['sl_dollar']})\n"
            f"RR: 1:{signal['rr']}\n"
            f"RSI: {signal['rsi']}\n"
            f"Volume: {vol}\n"
            f"Signal Time: {now_utc}")
    resp = requests.post(
        f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task",
        headers={"Content-Type": "application/json", "Authorization": CLICKUP_API_KEY},
        json={"name": f"🔔 {asset_name} — {signal['direction']} ({signal.get('conviction', '—')})",
              "description": desc, "status": "to do"},
        timeout=10)
    if resp.status_code in (200, 201):
        print("  ✅ ClickUp task created")
    else:
        print(f"  ❌ ClickUp error: {resp.status_code} — {resp.text}")

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
        name, symbol = asset["name"], asset["symbol"]
        print(f"\n▶ {name}")
        time.sleep(2)
        c15 = fetch_candles(symbol, "15min", 220)
        time.sleep(2)
        c4h = fetch_candles(symbol, "4h", 220)
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
            push_to_clickup(name, sig)
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
    print("🚀 Signal Engine started. Press Ctrl+C to stop.")
    while True:
        try:
            _run_once()
        except Exception as e:
            print(f"\n⚠ Run failed: {e} — retrying next cycle.", flush=True)
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
