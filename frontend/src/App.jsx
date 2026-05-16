import { useState, useEffect, useCallback } from "react";

const ASSETS = ["BTC", "ETH", "BCH", "GOLD", "SILVER", "OIL"];

const s = {
  page: { minHeight: "100vh", background: "#0a0a0f", color: "#e0e0e0", fontFamily: "'Courier New', monospace", padding: "24px 16px" },
  center: { textAlign: "center" },
  label: { fontSize: 10, letterSpacing: 6, color: "#444", marginBottom: 6 },
  h1: { fontSize: 24, fontWeight: 900, color: "#fff", margin: 0, letterSpacing: 2 },
  sub: { fontSize: 10, color: "#555", marginTop: 6 },
  tabRow: { display: "flex", justifyContent: "center", gap: 8, margin: "20px 0" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16, maxWidth: 1100, margin: "0 auto" },
  card: (active, color) => ({ background: "#0f0f1a", border: `1px solid ${active ? color + "44" : "#1a1a2e"}`, borderRadius: 8, padding: 20 }),
  cell: (bg) => ({ background: bg, borderRadius: 4, padding: "8px 10px" }),
  cellLabel: { fontSize: 9, color: "#555", marginBottom: 2 },
  cellVal: { fontSize: 13, color: "#fff" },
  statsGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 12, marginBottom: 28 },
  statCard: { background: "#0f0f1a", border: "1px solid #1a1a2e", borderRadius: 6, padding: 16, textAlign: "center" },
  statVal: (color) => ({ fontSize: 26, fontWeight: 900, color }),
  statLabel: { fontSize: 9, color: "#444", letterSpacing: 2, marginTop: 4 },
  sectionLabel: { fontSize: 10, letterSpacing: 4, color: "#444", marginBottom: 10 },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 10, background: "#0f0f1a", borderRadius: 6, overflow: "hidden", marginBottom: 24 },
  th: { padding: "10px 12px", color: "#444", textAlign: "left", borderBottom: "1px solid #1a1a2e", fontSize: 9, letterSpacing: 1 },
  td: { padding: "8px 12px", borderBottom: "1px solid #0a0a14" },
};

const dirColor = (dir) => ({ LONG: "#00e676", SHORT: "#ff5252", WATCHING: "#ffd740" }[dir] ?? "#888");
const convColor = (c) => ({ HC: "#00e676", MC: "#ffd740" }[c] ?? "#ff9800");
const accColor = (n) => n >= 60 ? "#00e676" : n >= 40 ? "#ffd740" : "#ff5252";

function Btn({ onClick, disabled, bg, children }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{
      background: bg ?? "#1565c0", color: "#fff", border: "none", borderRadius: 4,
      padding: "8px 20px", cursor: disabled ? "not-allowed" : "pointer",
      fontSize: 11, letterSpacing: 2, fontFamily: "inherit",
    }}>{children}</button>
  );
}

function OutcomeBadge({ outcome }) {
  const map = {
    TP: { bg: "#1b5e2044", color: "#00e676", label: "TP HIT" },
    SL: { bg: "#b71c1c44", color: "#ff5252", label: "SL HIT" },
  };
  const o = map[outcome] ?? { bg: "#1a1a2e", color: "#ffd740", label: "PENDING" };
  return (
    <span style={{ fontSize: 9, padding: "2px 8px", borderRadius: 3, background: o.bg, color: o.color }}>
      {o.label}
    </span>
  );
}

// ─── Live Signals Tab ────────────────────────────────────────────────────────

function SignalsTab() {
  const [signals, setSignals] = useState({});
  const [scanning, setScanning] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [pushing, setPushing] = useState({});
  const [pushed, setPushed] = useState({});

  const fetchSignals = useCallback(async () => {
    setScanning(true);
    try {
      const res = await fetch("/api/scan");
      setSignals(await res.json());
      setLastUpdated(new Date().toUTCString());
    } catch (e) {
      console.error("Scan failed:", e);
    }
    setScanning(false);
  }, []);

  useEffect(() => {
    fetchSignals();
    const t = setInterval(fetchSignals, 15 * 60 * 1000);
    return () => clearInterval(t);
  }, [fetchSignals]);

  const handlePush = async (name) => {
    const sig = signals[name];
    if (!sig || (sig.direction !== "LONG" && sig.direction !== "SHORT")) return;
    setPushing(p => ({ ...p, [name]: true }));
    try {
      await fetch("/api/push-clickup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ asset: name, signal: sig }),
      });
      setPushed(p => ({ ...p, [name]: true }));
      setTimeout(() => setPushed(p => ({ ...p, [name]: false })), 4000);
    } catch (e) {
      console.error("Push failed:", e);
    }
    setPushing(p => ({ ...p, [name]: false }));
  };

  return (
    <>
      <div style={{ ...s.center, marginBottom: 16 }}>
        <Btn onClick={fetchSignals} disabled={scanning} bg={scanning ? "#1a1a2e" : "#1565c0"}>
          {scanning ? "SCANNING..." : "⟳ SCAN NOW"}
        </Btn>
        {lastUpdated && (
          <div style={{ fontSize: 10, color: "#444", marginTop: 8 }}>
            Last scan: {lastUpdated} · Auto-refresh every 15 min
          </div>
        )}
      </div>

      <div style={s.grid}>
        {ASSETS.map(name => {
          const sig = signals[name];
          const actionable = sig?.direction === "LONG" || sig?.direction === "SHORT";
          return (
            <div key={name} style={s.card(actionable, dirColor(sig?.direction))}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                <div style={{ fontSize: 18, fontWeight: 900, color: "#fff", letterSpacing: 2 }}>{name}</div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: dirColor(sig?.direction), letterSpacing: 1 }}>
                    {sig ? sig.direction : "—"}
                  </div>
                  {sig?.conviction && (
                    <div style={{ fontSize: 10, color: convColor(sig.conviction), marginTop: 2 }}>{sig.conviction}</div>
                  )}
                </div>
              </div>

              {sig && sig.direction !== "ERROR" && (
                <>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 12 }}>
                    <div style={s.cell("#0a0a14")}>
                      <div style={s.cellLabel}>PRICE</div>
                      <div style={s.cellVal}>{sig.price?.toFixed(2) ?? "—"}</div>
                    </div>
                    <div style={s.cell("#0a0a14")}>
                      <div style={s.cellLabel}>RSI</div>
                      <div style={{ fontSize: 13, color: sig.rsi > 70 || sig.rsi < 30 ? "#ff5252" : "#fff" }}>
                        {sig.rsi?.toFixed(1) ?? "—"}
                      </div>
                    </div>
                    {actionable && (
                      <>
                        <div style={s.cell("#0a1a0a")}>
                          <div style={s.cellLabel}>TP</div>
                          <div style={{ fontSize: 13, color: "#00e676" }}>{sig.tp_price?.toFixed(2)}</div>
                        </div>
                        <div style={s.cell("#1a0a0a")}>
                          <div style={s.cellLabel}>SL</div>
                          <div style={{ fontSize: 13, color: "#ff5252" }}>{sig.sl_price?.toFixed(2)}</div>
                        </div>
                      </>
                    )}
                  </div>

                  <div style={{ fontSize: 10, color: sig.vol_above ? "#00e676" : "#ff5252", marginBottom: 8 }}>
                    VOL: {sig.vol_above ? "▲ Above Average" : "▼ Below Average"}
                  </div>

                  {actionable && (
                    <div style={{ fontSize: 10, color: "#555", marginBottom: 12 }}>
                      RR 1:{sig.rr} · TP ${sig.tp_dollar} · SL ${sig.sl_dollar?.toFixed(1)}
                    </div>
                  )}

                  {actionable && (
                    <Btn
                      onClick={() => handlePush(name)}
                      disabled={pushing[name]}
                      bg={pushed[name] ? "#1b5e20" : "#1565c0"}
                    >
                      {pushed[name] ? "✓ SENT" : pushing[name] ? "..." : "→ CLICKUP"}
                    </Btn>
                  )}
                </>
              )}

              {sig?.direction === "ERROR" && (
                <div style={{ fontSize: 10, color: "#ff5252" }}>Failed to fetch data</div>
              )}
              {!sig && (
                <div style={{ fontSize: 10, color: "#333" }}>{scanning ? "Scanning..." : "Click SCAN NOW"}</div>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}

// ─── History Tab ─────────────────────────────────────────────────────────────

function HistoryTab() {
  const [data, setData] = useState({ signals: [], stats: {} });
  const [loading, setLoading] = useState(false);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/history");
      setData(await res.json());
    } catch (e) {
      console.error("History failed:", e);
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const { signals, stats } = data;

  const statCards = [
    { label: "RESOLVED", val: stats.total ?? 0, color: "#fff" },
    { label: "TP HIT",   val: stats.tp ?? 0,    color: "#00e676" },
    { label: "SL HIT",   val: stats.sl ?? 0,    color: "#ff5252" },
    { label: "ACCURACY", val: `${stats.accuracy ?? 0}%`, color: accColor(stats.accuracy ?? 0) },
    { label: "PENDING",  val: stats.pending ?? 0, color: "#ffd740" },
  ];

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto" }}>
      {/* Summary cards */}
      <div style={s.statsGrid}>
        {statCards.map(({ label, val, color }) => (
          <div key={label} style={s.statCard}>
            <div style={s.statVal(color)}>{val}</div>
            <div style={s.statLabel}>{label}</div>
          </div>
        ))}
      </div>

      {/* By-asset accuracy */}
      {stats.by_asset && Object.keys(stats.by_asset).length > 0 && (
        <>
          <div style={s.sectionLabel}>ACCURACY BY ASSET</div>
          <table style={s.table}>
            <thead>
              <tr>{["ASSET", "TP", "SL", "ACCURACY"].map(h => <th key={h} style={s.th}>{h}</th>)}</tr>
            </thead>
            <tbody>
              {Object.entries(stats.by_asset).map(([asset, st]) => (
                <tr key={asset} style={{ borderBottom: "1px solid #0a0a14" }}>
                  <td style={{ ...s.td, color: "#fff", fontWeight: 700 }}>{asset}</td>
                  <td style={{ ...s.td, color: "#00e676" }}>{st.tp}</td>
                  <td style={{ ...s.td, color: "#ff5252" }}>{st.sl}</td>
                  <td style={{ ...s.td, color: accColor(st.accuracy), fontWeight: 700 }}>{st.accuracy}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {/* Signal table */}
      <div style={s.sectionLabel}>ALL SIGNALS</div>
      <div style={{ background: "#0f0f1a", border: "1px solid #1a1a2e", borderRadius: 8, overflow: "hidden", marginBottom: 16 }}>
        <table style={{ ...s.table, marginBottom: 0 }}>
          <thead>
            <tr>
              {["TIME", "ASSET", "DIR", "CONV", "ENTRY", "TP", "SL", "RR", "OUTCOME"].map(h => (
                <th key={h} style={s.th}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {signals.length === 0 ? (
              <tr><td colSpan={9} style={{ ...s.td, textAlign: "center", color: "#333", padding: 20 }}>No signals yet</td></tr>
            ) : (
              signals.slice(0, 50).map((r, i) => (
                <tr key={i} style={{ borderBottom: "1px solid #0a0a14" }}>
                  <td style={{ ...s.td, color: "#555", fontSize: 9 }}>{r.signal_time}</td>
                  <td style={{ ...s.td, color: "#fff", fontWeight: 700 }}>{r.asset}</td>
                  <td style={{ ...s.td, color: dirColor(r.direction) }}>{r.direction}</td>
                  <td style={{ ...s.td, color: "#ffd740" }}>{r.conviction ?? "—"}</td>
                  <td style={{ ...s.td, color: "#888" }}>{r.price}</td>
                  <td style={{ ...s.td, color: "#00e676" }}>{r.tp_price ?? "—"}</td>
                  <td style={{ ...s.td, color: "#ff5252" }}>{r.sl_price ?? "—"}</td>
                  <td style={{ ...s.td, color: "#888" }}>{r.rr ? `1:${r.rr}` : "—"}</td>
                  <td style={s.td}><OutcomeBadge outcome={r.outcome} /></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div style={s.center}>
        <Btn onClick={fetchHistory} disabled={loading} bg="#0f0f1a">
          {loading ? "LOADING..." : "⟳ REFRESH"}
        </Btn>
      </div>
    </div>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [tab, setTab] = useState("signals");

  return (
    <div style={s.page}>
      <div style={{ ...s.center, marginBottom: 8 }}>
        <div style={s.label}>PROP FIRM SIGNAL ENGINE</div>
        <h1 style={s.h1}>MOCK CAPITAL — PHASE 1</h1>
        <div style={s.sub}>Alligator · Heiken Ashi · RSI · Volume · EMA 50/200</div>
      </div>

      <div style={s.tabRow}>
        {[["signals", "LIVE SIGNALS"], ["history", "SIGNAL HISTORY"]].map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)} style={{
            background: tab === key ? "#1565c0" : "#0f0f1a",
            color: tab === key ? "#fff" : "#555",
            border: `1px solid ${tab === key ? "#1565c0" : "#1a1a2e"}`,
            borderRadius: 4, padding: "8px 20px", cursor: "pointer",
            fontSize: 11, letterSpacing: 2, fontFamily: "inherit",
          }}>{label}</button>
        ))}
      </div>

      {tab === "signals" ? <SignalsTab /> : <HistoryTab />}

      <div style={{ ...s.center, marginTop: 40, fontSize: 9, color: "#222", letterSpacing: 2 }}>
        MOCK CAPITAL · PHASE 1 · ALLIGATOR + HA + RSI + VOLUME + EMA · 1:1 NO LEVERAGE
      </div>
    </div>
  );
}
