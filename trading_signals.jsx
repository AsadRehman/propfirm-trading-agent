import { useState, useEffect, useCallback } from "react";

const TWELVE_DATA_KEY = "f1d53bcaa03a4c52bd0e8ac15129499c";
const CLICKUP_API_KEY = "pk_278549731_K5LBX7D3HU0V1CYSKU33NK4DRTQG5BRG";
const CLICKUP_LIST_ID = "901818156733";

const ASSETS = [
  { symbol: "BTC/USD", name: "BTC", source: "twelve", type: "crypto" },
  { symbol: "ETH/USD", name: "ETH", source: "twelve", type: "crypto" },
  { symbol: "BCH/USD", name: "BCH", source: "twelve", type: "crypto" },
  { symbol: "XAU/USD", name: "GOLD", source: "twelve", type: "metal" },
  { symbol: "XAG/USD", name: "SILVER", source: "twelve", type: "metal" },
  { symbol: "WTI/USD", name: "OIL", source: "twelve", type: "commodity" },
];

// --- Indicator calculations ---
function calcSMMA(data, period) {
  if (data.length < period) return [];
  const result = [];
  let sum = data.slice(0, period).reduce((a, b) => a + b, 0);
  result.push(sum / period);
  for (let i = period; i < data.length; i++) {
    const smma = (result[result.length - 1] * (period - 1) + data[i]) / period;
    result.push(smma);
  }
  return result;
}

function calcAlligator(closes) {
  const jaw = calcSMMA(closes, 13);
  const teeth = calcSMMA(closes, 8);
  const lips = calcSMMA(closes, 5);
  return { jaw, teeth, lips };
}

function calcHeikenAshi(candles) {
  const ha = [];
  for (let i = 0; i < candles.length; i++) {
    const c = candles[i];
    const haClose = (c.open + c.high + c.low + c.close) / 4;
    const haOpen = i === 0 ? (c.open + c.close) / 2 : (ha[i - 1].open + ha[i - 1].close) / 2;
    const haHigh = Math.max(c.high, haOpen, haClose);
    const haLow = Math.min(c.low, haOpen, haClose);
    ha.push({ open: haOpen, high: haHigh, low: haLow, close: haClose });
  }
  return ha;
}

function calcRSI(closes, period = 14) {
  if (closes.length < period + 1) return null;
  let gains = 0, losses = 0;
  for (let i = 1; i <= period; i++) {
    const diff = closes[i] - closes[i - 1];
    if (diff >= 0) gains += diff;
    else losses -= diff;
  }
  let avgGain = gains / period;
  let avgLoss = losses / period;
  for (let i = period + 1; i < closes.length; i++) {
    const diff = closes[i] - closes[i - 1];
    avgGain = (avgGain * (period - 1) + Math.max(diff, 0)) / period;
    avgLoss = (avgLoss * (period - 1) + Math.max(-diff, 0)) / period;
  }
  if (avgLoss === 0) return 100;
  const rs = avgGain / avgLoss;
  return 100 - 100 / (1 + rs);
}

function calcEMA(closes, period) {
  if (closes.length < period) return [];
  const k = 2 / (period + 1);
  const result = [closes.slice(0, period).reduce((a, b) => a + b, 0) / period];
  for (let i = period; i < closes.length; i++) {
    result.push(closes[i] * k + result[result.length - 1] * (1 - k));
  }
  return result;
}

function calcVolume(volumes) {
  if (volumes.length < 20) return null;
  const avg = volumes.slice(-20).reduce((a, b) => a + b, 0) / 20;
  const current = volumes[volumes.length - 1];
  return { current, avg, aboveAverage: current > avg };
}

// --- Signal analysis ---
function analyzeSignal(candles15m, candles4h) {
  if (!candles15m || candles15m.length < 30 || !candles4h || candles4h.length < 30) return null;

  const closes15m = candles15m.map(c => c.close);
  const closes4h = candles4h.map(c => c.close);
  const volumes15m = candles15m.map(c => c.volume);

  // Alligator 15m
  const alligator15m = calcAlligator(closes15m);
  const jawLast = alligator15m.jaw[alligator15m.jaw.length - 1];
  const teethLast = alligator15m.teeth[alligator15m.teeth.length - 1];
  const lipsLast = alligator15m.lips[alligator15m.lips.length - 1];
  const currentPrice = closes15m[closes15m.length - 1];

  // Alligator 4H
  const alligator4h = calcAlligator(closes4h);
  const jaw4hLast = alligator4h.jaw[alligator4h.jaw.length - 1];
  const teeth4hLast = alligator4h.teeth[alligator4h.teeth.length - 1];
  const lips4hLast = alligator4h.lips[alligator4h.lips.length - 1];

  // Heiken Ashi 15m
  const ha = calcHeikenAshi(candles15m);
  const haLast3 = ha.slice(-3);

  // RSI 15m
  const rsi = calcRSI(closes15m);

  // EMA 4H
  const ema50 = calcEMA(closes4h, 50);
  const ema200 = calcEMA(closes4h, 200);
  const ema50Last = ema50[ema50.length - 1];
  const ema200Last = ema200[ema200.length - 1];

  // Volume 15m
  const volume = calcVolume(volumes15m);

  if (!rsi || !volume || !ema50Last || !ema200Last) return null;

  // Direction checks
  const alligatorBullish15m = lipsLast > teethLast && teethLast > jawLast;
  const alligatorBearish15m = lipsLast < teethLast && teethLast < jawLast;
  const alligatorBullish4h = lips4hLast > teeth4hLast && teeth4hLast > jaw4hLast;
  const alligatorBearish4h = lips4hLast < teeth4hLast && teeth4hLast < jaw4hLast;
  const alligatorSleeping15m = Math.abs(lipsLast - jawLast) / jawLast < 0.001;

  const priceAboveAlligator = currentPrice > lipsLast && currentPrice > teethLast && currentPrice > jawLast;
  const priceBelowAlligator = currentPrice < lipsLast && currentPrice < teethLast && currentPrice < jawLast;

  const haBullish = haLast3.every(c => c.close > c.open);
  const haBearish = haLast3.every(c => c.close < c.open);
  const haHasLowerWicks = haLast3.some(c => (c.open - c.low) > (c.high - c.close) * 0.5);
  const haHasUpperWicks = haLast3.some(c => (c.high - c.close) > (c.open - c.low) * 0.5);

  const emaBullish = currentPrice > ema50Last && currentPrice > ema200Last;
  const emaBearish = currentPrice < ema50Last && currentPrice < ema200Last;
  const emaBetween = !emaBullish && !emaBearish;

  const rsiBullishRange = rsi > 50 && rsi < 70;
  const rsiBearishRange = rsi < 50 && rsi > 30;
  const rsiOverbought = rsi >= 70;
  const rsiOversold = rsi <= 30;

  // Separation strength for conviction
  const separation15m = Math.abs(lipsLast - jawLast) / jawLast;
  const separation4h = Math.abs(lips4hLast - jaw4hLast) / jaw4hLast;

  // Long signal
  let longScore = 0;
  let longConditions = [];
  if (emaBullish) { longScore++; longConditions.push("EMA Bullish ✅"); }
  if (alligatorBullish4h) { longScore++; longConditions.push("4H Alligator Up ✅"); }
  if (alligatorBullish15m && !alligatorSleeping15m) { longScore++; longConditions.push("15M Alligator Up ✅"); }
  if (priceAboveAlligator) { longScore++; longConditions.push("Price Above Lines ✅"); }
  if (haBullish && !haHasLowerWicks) { longScore++; longConditions.push("HA Clean Green ✅"); }
  if (rsiBullishRange) { longScore++; longConditions.push(`RSI ${rsi.toFixed(1)} ✅`); }
  if (volume.aboveAverage) { longScore++; longConditions.push("Volume Above Avg ✅"); }

  // Short signal
  let shortScore = 0;
  let shortConditions = [];
  if (emaBearish) { shortScore++; shortConditions.push("EMA Bearish ✅"); }
  if (alligatorBearish4h) { shortScore++; shortConditions.push("4H Alligator Down ✅"); }
  if (alligatorBearish15m && !alligatorSleeping15m) { shortScore++; shortConditions.push("15M Alligator Down ✅"); }
  if (priceBelowAlligator) { shortScore++; shortConditions.push("Price Below Lines ✅"); }
  if (haBearish && !haHasUpperWicks) { shortScore++; shortConditions.push("HA Clean Red ✅"); }
  if (rsiBearishRange) { shortScore++; shortConditions.push(`RSI ${rsi.toFixed(1)} ✅`); }
  if (volume.aboveAverage) { shortScore++; shortConditions.push("Volume Above Avg ✅"); }

  // Blockers
  const blocked = alligatorSleeping15m || emaBetween || rsiOverbought || rsiOversold;
  if (blocked) return { direction: "NO TRADE", score: 0, reason: "Blocked: sleeping/choppy/exhausted", currentPrice, rsi, volume };

  const isLong = longScore === 7;
  const isShort = shortScore === 7;

  if (!isLong && !isShort) {
    const bestScore = Math.max(longScore, shortScore);
    return { direction: "WATCHING", score: bestScore, currentPrice, rsi, volume, conditions: longScore > shortScore ? longConditions : shortConditions };
  }

  const direction = isLong ? "LONG" : "SHORT";
  const score = isLong ? longScore : shortScore;
  const conditions = isLong ? longConditions : shortConditions;

  // Conviction
  const strongSeparation = separation15m > 0.002 && separation4h > 0.002;
  const moderateSeparation = separation15m > 0.001;
  const cleanHA = isLong ? (haBullish && !haHasLowerWicks) : (haBearish && !haHasUpperWicks);
  const rsiStrong = isLong ? (rsi >= 55 && rsi <= 65) : (rsi >= 35 && rsi <= 45);

  let conviction = "LC";
  if (strongSeparation && cleanHA && rsiStrong) conviction = "HC";
  else if (moderateSeparation && cleanHA) conviction = "MC";

  // TP / SL based on conviction
  const rrMap = { HC: 2, MC: 1.5, LC: 1 };
  const tpMap = { HC: 25, MC: 20, LC: 15 };
  const rr = rrMap[conviction];
  const tpDollar = tpMap[conviction];
  const slDollar = tpDollar / rr;

  const priceMovePercent = tpDollar / 1000;
  const tpPrice = direction === "LONG"
    ? currentPrice * (1 + priceMovePercent)
    : currentPrice * (1 - priceMovePercent);
  const slPrice = direction === "LONG"
    ? currentPrice * (1 - (slDollar / 1000))
    : currentPrice * (1 + (slDollar / 1000));

  return {
    direction,
    conviction,
    score,
    currentPrice,
    tpPrice,
    slPrice,
    tpDollar,
    slDollar,
    rr,
    rsi,
    volume,
    conditions,
  };
}

// --- Fetch candles from Twelve Data ---
async function fetchCandles(symbol, interval, outputSize = 200) {
  const url = `https://api.twelvedata.com/time_series?symbol=${encodeURIComponent(symbol)}&interval=${interval}&outputsize=${outputSize}&apikey=${TWELVE_DATA_KEY}`;
  const res = await fetch(url);
  const data = await res.json();
  if (!data.values) return null;
  return data.values.reverse().map(v => ({
    open: parseFloat(v.open),
    high: parseFloat(v.high),
    low: parseFloat(v.low),
    close: parseFloat(v.close),
    volume: parseFloat(v.volume || 1000),
  }));
}

// --- Push to ClickUp ---
async function pushToClickUp(asset, signal, signalTime) {
  const volumeLabel = signal.volume?.aboveAverage ? "Above Average" : "Below Average";
  const description =
    `Asset: ${asset}\n` +
    `Direction: ${signal.direction}\n` +
    `Current Price: ${signal.currentPrice?.toFixed(4)}\n` +
    `TP: ${signal.tpPrice?.toFixed(4)}\n` +
    `SL: ${signal.slPrice?.toFixed(4)}\n` +
    `Volume: ${volumeLabel}\n` +
    `Signal Time: ${signalTime}`;

  const body = {
    name: `🔔 ${asset} — ${signal.direction} Signal`,
    description,
    status: "to do",
  };

  await fetch(`https://api.clickup.com/api/v2/list/${CLICKUP_LIST_ID}/task`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: CLICKUP_API_KEY,
    },
    body: JSON.stringify(body),
  });
}

// --- Trade memory for learning layer ---
function getTradeMemory() {
  try {
    const raw = localStorage.getItem("trade_memory");
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveTradeMemory(memory) {
  try { localStorage.setItem("trade_memory", JSON.stringify(memory)); } catch {}
}

// --- Main App ---
export default function App() {
  const [signals, setSignals] = useState({});
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [pushingClickUp, setPushingClickUp] = useState({});
  const [pushed, setPushed] = useState({});
  const [tradeLog, setTradeLog] = useState(getTradeMemory());
  const [logAsset, setLogAsset] = useState(null);
  const [logResult, setLogResult] = useState("WIN");

  const fetchAllSignals = useCallback(async () => {
    setLoading(true);
    const results = {};
    for (const asset of ASSETS) {
      try {
        const [candles15m, candles4h] = await Promise.all([
          fetchCandles(asset.symbol, "15min", 220),
          fetchCandles(asset.symbol, "4h", 220),
        ]);
        const signal = analyzeSignal(candles15m, candles4h);
        results[asset.name] = { ...signal, symbol: asset.symbol };
      } catch (e) {
        results[asset.name] = { direction: "ERROR", error: e.message };
      }
    }
    setSignals(results);
    setLastUpdated(new Date().toUTCString());
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchAllSignals();
    const interval = setInterval(fetchAllSignals, 15 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchAllSignals]);

  const handlePushClickUp = async (assetName) => {
    const signal = signals[assetName];
    if (!signal || signal.direction !== "LONG" && signal.direction !== "SHORT") return;
    setPushingClickUp(p => ({ ...p, [assetName]: true }));
    const time = new Date().toUTCString();
    await pushToClickUp(assetName, signal, time);
    setPushingClickUp(p => ({ ...p, [assetName]: false }));
    setPushed(p => ({ ...p, [assetName]: true }));
    setTimeout(() => setPushed(p => ({ ...p, [assetName]: false })), 4000);
  };

  const handleLogTrade = (assetName) => {
    const signal = signals[assetName];
    if (!signal) return;
    const entry = {
      date: new Date().toISOString(),
      asset: assetName,
      direction: signal.direction,
      conviction: signal.conviction,
      rsi: signal.rsi,
      volumeAbove: signal.volume?.aboveAverage,
      result: logResult,
      price: signal.currentPrice,
    };
    const updated = [entry, ...tradeLog].slice(0, 100);
    setTradeLog(updated);
    saveTradeMemory(updated);
    setLogAsset(null);
  };

  // Learning layer: asset performance score
  function getAssetScore(assetName) {
    const trades = tradeLog.filter(t => t.asset === assetName);
    if (trades.length === 0) return null;
    const wins = trades.filter(t => t.result === "WIN").length;
    return `${wins}W / ${trades.length - wins}L`;
  }

  const directionColor = (dir) => {
    if (dir === "LONG") return "#00e676";
    if (dir === "SHORT") return "#ff5252";
    if (dir === "WATCHING") return "#ffd740";
    return "#888";
  };

  const convictionColor = (c) => {
    if (c === "HC") return "#00e676";
    if (c === "MC") return "#ffd740";
    return "#ff9800";
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0a0a0f",
      color: "#e0e0e0",
      fontFamily: "'Courier New', monospace",
      padding: "24px 16px",
    }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 32 }}>
        <div style={{ fontSize: 11, letterSpacing: 6, color: "#444", marginBottom: 8 }}>PROP FIRM SIGNAL ENGINE</div>
        <h1 style={{ fontSize: 26, fontWeight: 900, color: "#fff", margin: 0, letterSpacing: 2 }}>
          MOCK CAPITAL — PHASE 1
        </h1>
        <div style={{ fontSize: 11, color: "#555", marginTop: 8 }}>
          Alligator · Heiken Ashi · RSI · Volume · EMA50/200
        </div>
        <div style={{ marginTop: 16, display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
          <button
            onClick={fetchAllSignals}
            disabled={loading}
            style={{
              background: loading ? "#1a1a2e" : "#1565c0",
              color: "#fff",
              border: "none",
              borderRadius: 4,
              padding: "10px 24px",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: 12,
              letterSpacing: 2,
              fontFamily: "inherit",
            }}
          >
            {loading ? "SCANNING..." : "⟳ SCAN NOW"}
          </button>
        </div>
        {lastUpdated && (
          <div style={{ fontSize: 10, color: "#444", marginTop: 8 }}>
            Last scan: {lastUpdated} · Auto-refresh every 15 min
          </div>
        )}
      </div>

      {/* Signal Cards */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
        gap: 16,
        maxWidth: 1100,
        margin: "0 auto",
      }}>
        {ASSETS.map(asset => {
          const sig = signals[asset.name];
          const score = getAssetScore(asset.name);
          const isActionable = sig?.direction === "LONG" || sig?.direction === "SHORT";

          return (
            <div key={asset.name} style={{
              background: "#0f0f1a",
              border: `1px solid ${isActionable ? directionColor(sig?.direction) + "44" : "#1a1a2e"}`,
              borderRadius: 8,
              padding: 20,
              position: "relative",
              transition: "border-color 0.3s",
            }}>
              {/* Asset header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                <div>
                  <div style={{ fontSize: 18, fontWeight: 900, color: "#fff", letterSpacing: 2 }}>{asset.name}</div>
                  <div style={{ fontSize: 10, color: "#444", marginTop: 2 }}>{asset.symbol}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: directionColor(sig?.direction),
                    letterSpacing: 1,
                  }}>
                    {sig ? sig.direction : "—"}
                  </div>
                  {sig?.conviction && (
                    <div style={{
                      fontSize: 10,
                      color: convictionColor(sig.conviction),
                      marginTop: 2,
                    }}>{sig.conviction}</div>
                  )}
                </div>
              </div>

              {sig && sig.direction !== "ERROR" && (
                <>
                  {/* Price info */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 12 }}>
                    <div style={{ background: "#0a0a14", borderRadius: 4, padding: "8px 10px" }}>
                      <div style={{ fontSize: 9, color: "#555", marginBottom: 2 }}>PRICE</div>
                      <div style={{ fontSize: 13, color: "#fff" }}>{sig.currentPrice?.toFixed(2) ?? "—"}</div>
                    </div>
                    <div style={{ background: "#0a0a14", borderRadius: 4, padding: "8px 10px" }}>
                      <div style={{ fontSize: 9, color: "#555", marginBottom: 2 }}>RSI</div>
                      <div style={{ fontSize: 13, color: sig.rsi > 70 || sig.rsi < 30 ? "#ff5252" : "#fff" }}>
                        {sig.rsi?.toFixed(1) ?? "—"}
                      </div>
                    </div>
                    {isActionable && (
                      <>
                        <div style={{ background: "#0a1a0a", borderRadius: 4, padding: "8px 10px" }}>
                          <div style={{ fontSize: 9, color: "#555", marginBottom: 2 }}>TP</div>
                          <div style={{ fontSize: 13, color: "#00e676" }}>{sig.tpPrice?.toFixed(2)}</div>
                        </div>
                        <div style={{ background: "#1a0a0a", borderRadius: 4, padding: "8px 10px" }}>
                          <div style={{ fontSize: 9, color: "#555", marginBottom: 2 }}>SL</div>
                          <div style={{ fontSize: 13, color: "#ff5252" }}>{sig.slPrice?.toFixed(2)}</div>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Volume */}
                  <div style={{
                    fontSize: 10,
                    color: sig.volume?.aboveAverage ? "#00e676" : "#ff5252",
                    marginBottom: 10,
                  }}>
                    VOL: {sig.volume?.aboveAverage ? "▲ Above Average" : "▼ Below Average"}
                  </div>

                  {/* Conditions */}
                  {sig.conditions && (
                    <div style={{ marginBottom: 12 }}>
                      {sig.conditions.map((c, i) => (
                        <div key={i} style={{ fontSize: 9, color: "#666", lineHeight: 1.8 }}>{c}</div>
                      ))}
                    </div>
                  )}

                  {/* Learning score */}
                  {score && (
                    <div style={{ fontSize: 9, color: "#444", marginBottom: 10 }}>
                      HISTORY: {score}
                    </div>
                  )}

                  {/* Actions */}
                  {isActionable && (
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      <button
                        onClick={() => handlePushClickUp(asset.name)}
                        disabled={pushingClickUp[asset.name]}
                        style={{
                          background: pushed[asset.name] ? "#1b5e20" : "#1565c0",
                          color: "#fff",
                          border: "none",
                          borderRadius: 4,
                          padding: "7px 14px",
                          cursor: "pointer",
                          fontSize: 10,
                          letterSpacing: 1,
                          fontFamily: "inherit",
                        }}
                      >
                        {pushed[asset.name] ? "✓ SENT" : pushingClickUp[asset.name] ? "..." : "→ CLICKUP"}
                      </button>
                      <button
                        onClick={() => setLogAsset(logAsset === asset.name ? null : asset.name)}
                        style={{
                          background: "#1a1a2e",
                          color: "#aaa",
                          border: "1px solid #2a2a4e",
                          borderRadius: 4,
                          padding: "7px 14px",
                          cursor: "pointer",
                          fontSize: 10,
                          letterSpacing: 1,
                          fontFamily: "inherit",
                        }}
                      >
                        LOG TRADE
                      </button>
                    </div>
                  )}

                  {/* Log trade panel */}
                  {logAsset === asset.name && (
                    <div style={{ marginTop: 12, background: "#0a0a14", borderRadius: 4, padding: 12 }}>
                      <div style={{ fontSize: 10, color: "#888", marginBottom: 8 }}>TRADE RESULT</div>
                      <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
                        {["WIN", "LOSS", "BE"].map(r => (
                          <button
                            key={r}
                            onClick={() => setLogResult(r)}
                            style={{
                              background: logResult === r ? (r === "WIN" ? "#1b5e20" : r === "LOSS" ? "#b71c1c" : "#333") : "#1a1a2e",
                              color: "#fff",
                              border: "none",
                              borderRadius: 4,
                              padding: "6px 12px",
                              cursor: "pointer",
                              fontSize: 10,
                              fontFamily: "inherit",
                            }}
                          >{r}</button>
                        ))}
                      </div>
                      <button
                        onClick={() => handleLogTrade(asset.name)}
                        style={{
                          background: "#283593",
                          color: "#fff",
                          border: "none",
                          borderRadius: 4,
                          padding: "7px 16px",
                          cursor: "pointer",
                          fontSize: 10,
                          fontFamily: "inherit",
                        }}
                      >SAVE</button>
                    </div>
                  )}
                </>
              )}

              {sig?.direction === "ERROR" && (
                <div style={{ fontSize: 10, color: "#ff5252" }}>Failed to fetch data</div>
              )}

              {!sig && (
                <div style={{ fontSize: 10, color: "#333" }}>Scanning...</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Trade History */}
      {tradeLog.length > 0 && (
        <div style={{ maxWidth: 1100, margin: "32px auto 0" }}>
          <div style={{ fontSize: 11, letterSpacing: 4, color: "#444", marginBottom: 12 }}>TRADE HISTORY</div>
          <div style={{ background: "#0f0f1a", border: "1px solid #1a1a2e", borderRadius: 8, overflow: "hidden" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 10 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid #1a1a2e" }}>
                  {["DATE", "ASSET", "DIR", "CONVICTION", "RSI", "VOLUME", "RESULT"].map(h => (
                    <th key={h} style={{ padding: "10px 12px", color: "#444", textAlign: "left", letterSpacing: 1 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tradeLog.slice(0, 10).map((t, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #0a0a14" }}>
                    <td style={{ padding: "8px 12px", color: "#555" }}>{new Date(t.date).toLocaleDateString()}</td>
                    <td style={{ padding: "8px 12px", color: "#fff", fontWeight: 700 }}>{t.asset}</td>
                    <td style={{ padding: "8px 12px", color: directionColor(t.direction) }}>{t.direction}</td>
                    <td style={{ padding: "8px 12px", color: convictionColor(t.conviction) }}>{t.conviction}</td>
                    <td style={{ padding: "8px 12px", color: "#888" }}>{t.rsi?.toFixed(1)}</td>
                    <td style={{ padding: "8px 12px", color: t.volumeAbove ? "#00e676" : "#ff5252" }}>{t.volumeAbove ? "▲" : "▼"}</td>
                    <td style={{ padding: "8px 12px", color: t.result === "WIN" ? "#00e676" : t.result === "LOSS" ? "#ff5252" : "#ffd740" }}>{t.result}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div style={{ textAlign: "center", marginTop: 32, fontSize: 9, color: "#222", letterSpacing: 2 }}>
        MOCK CAPITAL · PHASE 1 · ALLIGATOR + HA + RSI + VOLUME + EMA · 1:1 NO LEVERAGE
      </div>
    </div>
  );
}
