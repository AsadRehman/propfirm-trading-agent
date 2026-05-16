"""
Mock Capital Phase 1 — Signal Engine
Assets: BTC, ETH, BCH, Gold, Silver, Crude Oil
Indicators: Williams Alligator + Heiken Ashi + RSI + Volume + EMA 50/200
Runs every 15 minutes via GitHub Actions
- Pushes signals to ClickUp
- Saves every signal to signal_history.json
- Auto-checks pending signals for TP/SL outcome
- Generates dashboard.html with accuracy tracking
"""

import os
import json
import time
import requests
from datetime import datetime, timezone

# --- Config ---
TWELVE_DATA_KEY = os.environ["TWELVE_DATA_API_KEY"]
CLICKUP_API_KEY = os.environ["CLICKUP_API_KEY"]
CLICKUP_LIST_ID = os.environ["CLICKUP_LIST_ID"]
HISTORY_FILE    = "signal_history.json"

ASSETS = [
    {"name": "BTC",    "symbol": "BTC/USD"},
    {"name": "ETH",    "symbol": "ETH/USD"},
    {"name": "BCH",    "symbol": "BCH/USD"},
    {"name": "GOLD",   "symbol": "XAU/USD"},
    {"name": "SILVER", "symbol": "XAG/USD"},
    {"name": "OIL",    "symbol": "WTI/USD"},
]

# ─────────────────────────────────────────
# INDICATORS
# ─────────────────────────────────────────

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

# ─────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────

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

# ─────────────────────────────────────────
# SIGNAL ANALYSIS
# ─────────────────────────────────────────

def analyze_signal(c15, c4h):
    if not c15 or len(c15) < 50 or not c4h or len(c4h) < 210:
        return None

    cl15 = [c["close"] for c in c15]
    cl4h = [c["close"] for c in c4h]
    vols = [c["volume"] for c in c15]

    j15, t15, l15 = calc_alligator(cl15)
    j4h, t4h, l4h = calc_alligator(cl4h)
    price = cl15[-1]

    jl, tl, ll       = j15[-1], t15[-1], l15[-1]
    j4, t4, l4       = j4h[-1], t4h[-1], l4h[-1]

    ha   = calc_heiken_ashi(c15)
    h3   = ha[-3:]
    hbull = all(c["close"] > c["open"] for c in h3)
    hbear = all(c["close"] < c["open"] for c in h3)
    hlw  = any((c["open"]-c["low"]) > (c["high"]-c["close"])*0.5 for c in h3)
    huw  = any((c["high"]-c["close"]) > (c["open"]-c["low"])*0.5 for c in h3)

    rsi = calc_rsi(cl15)
    if rsi is None: return None

    e50  = calc_ema(cl4h, 50)
    e200 = calc_ema(cl4h, 200)
    if not e50 or not e200: return None
    e50l, e200l = e50[-1], e200[-1]

    vol_ab   = volume_above_avg(vols)
    sleeping = abs(ll - jl) / jl < 0.001
    ema_bull = price > e50l and price > e200l
    ema_bear = price < e50l and price < e200l
    ema_btw  = not ema_bull and not ema_bear

    if sleeping or ema_btw or rsi >= 70 or rsi <= 30:
        return {"direction": "NO TRADE", "price": round(price,4), "rsi": round(rsi,2), "vol_above": vol_ab}

    bull15 = ll > tl > jl
    bear15 = ll < tl < jl
    bull4h = l4 > t4 > j4
    bear4h = l4 < t4 < j4
    pabove = price > ll and price > tl and price > jl
    pbelow = price < ll and price < tl and price < jl

    ls = sum([ema_bull, bull4h, bull15 and not sleeping, pabove,
              hbull and not hlw, 50<rsi<70, vol_ab])
    ss = sum([ema_bear, bear4h, bear15 and not sleeping, pbelow,
              hbear and not huw, 30<rsi<50, vol_ab])

    if ls < 7 and ss < 7:
        return {"direction": "WATCHING", "price": round(price,4), "rsi": round(rsi,2), "vol_above": vol_ab}

    direction = "LONG" if ls == 7 else "SHORT"
    sep15 = abs(ll - jl) / jl
    sep4h = abs(l4 - j4) / j4
    cha   = (hbull and not hlw) if direction=="LONG" else (hbear and not huw)
    rsis  = (55<=rsi<=65) if direction=="LONG" else (35<=rsi<=45)

    conviction = "HC" if sep15>0.002 and sep4h>0.002 and cha and rsis else \
                 "MC" if sep15>0.001 and cha else "LC"

    rr  = {"HC":2.0,"MC":1.5,"LC":1.0}[conviction]
    tpd = {"HC":25, "MC":20, "LC":15 }[conviction]
    sld = round(tpd/rr, 2)
    pct = tpd/1000
    tpp = price*(1+pct) if direction=="LONG" else price*(1-pct)
    slp = price*(1-sld/1000) if direction=="LONG" else price*(1+sld/1000)

    return {"direction": direction, "conviction": conviction,
            "price": round(price,4), "tp_price": round(tpp,4),
            "sl_price": round(slp,4), "tp_dollar": tpd,
            "sl_dollar": sld, "rr": rr,
            "rsi": round(rsi,2), "vol_above": vol_ab}

# ─────────────────────────────────────────
# OUTCOME CHECKER
# ─────────────────────────────────────────

def check_pending_outcomes(history, candles_map):
    updated = False
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    for record in history:
        if record["outcome"] != "PENDING":
            continue
        candles = candles_map.get(record["asset"])
        if not candles:
            continue
        direction = record["direction"]
        tp = record["tp_price"]
        sl = record["sl_price"]
        for c in candles[-50:]:
            if direction == "LONG":
                if c["high"] >= tp:
                    record.update({"outcome":"TP","outcome_time":now_utc,"outcome_price":tp})
                    updated = True
                    print(f"  🎯 TP HIT: {record['asset']} LONG @ {tp}")
                    break
                elif c["low"] <= sl:
                    record.update({"outcome":"SL","outcome_time":now_utc,"outcome_price":sl})
                    updated = True
                    print(f"  ❌ SL HIT: {record['asset']} LONG @ {sl}")
                    break
            elif direction == "SHORT":
                if c["low"] <= tp:
                    record.update({"outcome":"TP","outcome_time":now_utc,"outcome_price":tp})
                    updated = True
                    print(f"  🎯 TP HIT: {record['asset']} SHORT @ {tp}")
                    break
                elif c["high"] >= sl:
                    record.update({"outcome":"SL","outcome_time":now_utc,"outcome_price":sl})
                    updated = True
                    print(f"  ❌ SL HIT: {record['asset']} SHORT @ {sl}")
                    break
    return history, updated

# ─────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def record_signal(history, asset_name, signal):
    now_utc   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    signal_id = f"{asset_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
    # deduplicate within same hour
    for r in history[:12]:
        if r["id"].startswith(f"{asset_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H')}"):
            print(f"  ⏭ Duplicate skipped for {asset_name}")
            return history
    history.insert(0, {
        "id": signal_id, "asset": asset_name,
        "direction": signal["direction"], "conviction": signal.get("conviction","—"),
        "price": signal["price"], "tp_price": signal.get("tp_price"),
        "sl_price": signal.get("sl_price"), "tp_dollar": signal.get("tp_dollar"),
        "sl_dollar": signal.get("sl_dollar"), "rr": signal.get("rr"),
        "rsi": signal.get("rsi"), "vol_above": signal.get("vol_above"),
        "signal_time": now_utc, "outcome": "PENDING",
        "outcome_time": None, "outcome_price": None,
    })
    return history

# ─────────────────────────────────────────
# CLICKUP
# ─────────────────────────────────────────

def push_to_clickup(asset_name, signal):
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    desc = (f"Asset: {asset_name}\n"
            f"Direction: {signal['direction']}\n"
            f"Current Price: {signal['price']}\n"
            f"TP: {signal['tp_price']}\n"
            f"SL: {signal['sl_price']}\n"
            f"Volume: {'Above Average' if signal['vol_above'] else 'Below Average'}\n"
            f"Signal Time: {now_utc}")
    resp = requests.post(
        f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task",
        headers={"Content-Type":"application/json","Authorization":CLICKUP_API_KEY},
        json={"name":f"🔔 {asset_name} — {signal['direction']} ({signal.get('conviction','—')})",
              "description":desc,"status":"to do"},
        timeout=10)
    if resp.status_code in (200,201):
        print(f"  ✅ ClickUp task created")
    else:
        print(f"  ❌ ClickUp error: {resp.status_code}")

# ─────────────────────────────────────────
# ACCURACY
# ─────────────────────────────────────────

def calc_accuracy(history):
    resolved = [r for r in history if r["outcome"] in ("TP","SL")]
    if not resolved:
        return {"total":0,"tp":0,"sl":0,"accuracy":0,"pending":len([r for r in history if r["outcome"]=="PENDING"]),"by_asset":{}}
    tp = sum(1 for r in resolved if r["outcome"]=="TP")
    sl = len(resolved) - tp
    by_asset = {}
    for r in resolved:
        a = r["asset"]
        if a not in by_asset: by_asset[a] = {"tp":0,"sl":0}
        by_asset[a][r["outcome"].lower()] += 1
    for a in by_asset:
        t,s = by_asset[a]["tp"], by_asset[a]["sl"]
        by_asset[a]["accuracy"] = round(t/(t+s)*100,1)
    return {"total":len(resolved),"tp":tp,"sl":sl,
            "accuracy":round(tp/len(resolved)*100,1),
            "pending":len([r for r in history if r["outcome"]=="PENDING"]),
            "by_asset":by_asset}

# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

def generate_dashboard(history):
    stats   = calc_accuracy(history)
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pending  = [r for r in history if r["outcome"]=="PENDING"]
    resolved = [r for r in history if r["outcome"] in ("TP","SL")]

    def badge(o):
        if o=="TP":      return '<span class="badge tp">🎯 TP HIT</span>'
        if o=="SL":      return '<span class="badge sl">❌ SL HIT</span>'
        return '<span class="badge pend">⏳ PENDING</span>'

    def rows(recs):
        if not recs: return '<tr><td colspan="9" class="empty">No signals yet</td></tr>'
        out = ""
        for r in recs:
            dc = "long" if r["direction"]=="LONG" else "short"
            out += (f'<tr>'
                    f'<td class="mono">{r["signal_time"]}</td>'
                    f'<td class="asset">{r["asset"]}</td>'
                    f'<td class="{dc}">{r["direction"]}</td>'
                    f'<td class="conv">{r["conviction"]}</td>'
                    f'<td class="mono">{r["price"]}</td>'
                    f'<td class="tpv">{r["tp_price"] or "—"}</td>'
                    f'<td class="slv">{r["sl_price"] or "—"}</td>'
                    f'<td>{badge(r["outcome"])}</td>'
                    f'<td class="mono dim">{r["outcome_time"] or "—"}</td>'
                    f'</tr>')
        return out

    asset_rows = ""
    for a, s in stats.get("by_asset",{}).items():
        acc = s["accuracy"]
        col = "#00e676" if acc>=60 else "#ffd740" if acc>=40 else "#ff5252"
        asset_rows += (f'<tr><td class="asset">{a}</td>'
                       f'<td>{s["tp"]}</td><td>{s["sl"]}</td>'
                       f'<td style="color:{col};font-weight:700">{acc}%</td></tr>')

    acc_color = "green" if stats["accuracy"]>=60 else "yellow" if stats["accuracy"]>=40 else "red"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mock Capital — Signal Dashboard</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#080810;color:#ccc;font-family:'Courier New',monospace;padding:24px 16px}}
h1{{color:#fff;font-size:20px;letter-spacing:3px;margin-bottom:4px}}
.sub{{font-size:10px;color:#444;letter-spacing:2px;margin-bottom:4px}}
.upd{{font-size:9px;color:#333;margin-bottom:28px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin-bottom:28px}}
.card{{background:#0f0f1a;border:1px solid #1a1a2e;border-radius:6px;padding:16px;text-align:center}}
.val{{font-size:28px;font-weight:900;color:#fff}}
.val.green{{color:#00e676}}.val.red{{color:#ff5252}}.val.yellow{{color:#ffd740}}
.lbl{{font-size:9px;color:#444;letter-spacing:2px;margin-top:4px}}
.sec{{font-size:10px;letter-spacing:4px;color:#444;margin:24px 0 10px}}
table{{width:100%;border-collapse:collapse;font-size:11px;background:#0f0f1a;border-radius:6px;overflow:hidden;margin-bottom:8px}}
th{{padding:10px 12px;color:#444;text-align:left;border-bottom:1px solid #1a1a2e;font-size:9px;letter-spacing:1px}}
td{{padding:8px 12px;border-bottom:1px solid #0a0a14}}
.asset{{color:#fff;font-weight:700}}.long{{color:#00e676}}.short{{color:#ff5252}}
.conv{{color:#ffd740}}.tpv{{color:#00e676}}.slv{{color:#ff5252}}
.mono{{font-family:monospace;color:#888;font-size:10px}}.dim{{color:#444}}
.empty{{color:#333;text-align:center;padding:20px}}
.badge{{font-size:10px;padding:2px 8px;border-radius:3px}}
.badge.tp{{background:#1b5e2044;color:#00e676}}
.badge.sl{{background:#b71c1c44;color:#ff5252}}
.badge.pend{{background:#1a1a2e;color:#ffd740}}
</style>
</head>
<body>
<h1>MOCK CAPITAL — PHASE 1</h1>
<div class="sub">SIGNAL ACCURACY TRACKER</div>
<div class="upd">Last updated: {now_utc} · Auto-updates every 15 min</div>

<div class="grid">
  <div class="card"><div class="val">{stats['total']}</div><div class="lbl">RESOLVED</div></div>
  <div class="card"><div class="val green">{stats['tp']}</div><div class="lbl">TP HIT</div></div>
  <div class="card"><div class="val red">{stats['sl']}</div><div class="lbl">SL HIT</div></div>
  <div class="card"><div class="val {acc_color}">{stats['accuracy']}%</div><div class="lbl">ACCURACY</div></div>
  <div class="card"><div class="val yellow">{stats['pending']}</div><div class="lbl">PENDING</div></div>
</div>

<div class="sec">ACCURACY BY ASSET</div>
<table>
  <thead><tr><th>ASSET</th><th>TP</th><th>SL</th><th>ACCURACY</th></tr></thead>
  <tbody>{asset_rows or '<tr><td colspan="4" class="empty">No resolved signals yet</td></tr>'}</tbody>
</table>

<div class="sec">PENDING SIGNALS</div>
<table>
  <thead><tr><th>SIGNAL TIME</th><th>ASSET</th><th>DIR</th><th>CONV</th><th>ENTRY</th><th>TP</th><th>SL</th><th>STATUS</th><th>RESOLVED AT</th></tr></thead>
  <tbody>{rows(pending)}</tbody>
</table>

<div class="sec">RESOLVED SIGNALS</div>
<table>
  <thead><tr><th>SIGNAL TIME</th><th>ASSET</th><th>DIR</th><th>CONV</th><th>ENTRY</th><th>TP</th><th>SL</th><th>STATUS</th><th>RESOLVED AT</th></tr></thead>
  <tbody>{rows(resolved[:100])}</tbody>
</table>
</body></html>"""

    with open("dashboard.html","w") as f:
        f.write(html)
    print("  📊 dashboard.html updated")

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*55}\nSignal Engine — {now}\n{'='*55}")

    history     = load_history()
    candles_map = {}

    for asset in ASSETS:
        name, symbol = asset["name"], asset["symbol"]
        print(f"\n▶ {name}")
        time.sleep(2)
        c15 = fetch_candles(symbol, "15min", 220)
        time.sleep(2)
        c4h = fetch_candles(symbol, "4h",   220)
        if not c15 or not c4h:
            print(f"  ⚠ Skipping")
            continue
        candles_map[name] = c15
        sig = analyze_signal(c15, c4h)
        if not sig:
            print(f"  — Insufficient data")
            continue
        print(f"  {sig['direction']} | Price:{sig['price']} | RSI:{sig['rsi']} | Vol:{'▲' if sig['vol_above'] else '▼'}")
        if sig["direction"] in ("LONG","SHORT"):
            print(f"  Conviction:{sig['conviction']} TP:{sig['tp_price']} SL:{sig['sl_price']} RR:1:{sig['rr']}")
            history = record_signal(history, name, sig)
            push_to_clickup(name, sig)
        else:
            print(f"  → {sig['direction']}")

    print(f"\n{'─'*55}\nChecking pending outcomes...")
    history, _ = check_pending_outcomes(history, candles_map)

    save_history(history)
    generate_dashboard(history)
    print(f"\n{'='*55}\nDone.\n{'='*55}\n")

if __name__ == "__main__":
    main()
