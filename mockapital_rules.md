# 🏦 Mock Capital — Phase 1 Rules (MockRace 2-Step)
> **Account:** $10,000 | **Platform:** MTR (MatchTrader) | **Type:** Swap-Free | **Add-ons:** News Trading & Weekend Holding | **Leverage:** 1:1 (no leverage)

---

## 📊 Phase 1 Targets

| Parameter | Value |
|---|---|
| **Profit Target** | 8% → **$800** |
| **Overall Drawdown** | 10% → **$1,000 max loss** |
| **Daily Drawdown** | 5% → **$500 per day** |
| **Min Trading Days** | 3 days |
| **Time Limit** | No Limit |
| **Leverage** | Not used — trading 1:1 only |

---

## ⚠️ Hard Breach Rules (Instant Account Closure)

These violations result in **immediate, permanent, no-appeal account closure**:

- **Daily Loss Limit exceeded** — equity + floating PnL drops more than 5% ($500) in a single session
- **Overall Drawdown exceeded** — account balance or equity drops below $9,000 (10% from $10k)
- **Account inactive for 30 days** — hard breach, permanently disabled

---

## 📅 Daily Loss Limit — Critical Detail

- **Limit:** 5% of starting balance = **$500 per day**
- **Calculation:** Closed P&L + floating (open) P&L combined — both count at all times
- **Reset time (MTR platform):** Daily resets at **22:00 UTC** — this is your new trading day start
- **Your safe operational limit:** Stop trading at **$350 daily loss (3.5%)** — leaves $150 buffer before hard breach

---

## 📉 Overall Drawdown

- **Limit:** 10% of initial account = **$1,000 total**
- **Type:** Static — does NOT trail. Floor is fixed at $9,000 regardless of profits made
- **Floor:** Account equity/balance must never go below **$9,000**
- **Includes:** Floating positions, closed trades, commissions
- **Your personal floor:** Treat **$9,400 (6% loss = $600)** as your personal stop — gives $400 buffer to the hard breach

---

## ⏱️ Trade Duration Rule

- **Rule:** Average trade duration across ALL trades must exceed **2 minutes**
- **Also:** Minimum 50% of total profit must come from trades lasting longer than 2 minutes
- **Consequence of breach:** Free reset to Phase 1 (not a hard breach, but wastes time and fees)
- **Your safe minimum:** Hold trades for at least **3 minutes** per entry
- **Ideal hold time:** 15 minutes to 4H for BTC, ETH, Gold — suits 1:1 trading naturally

---

## 📰 News Trading (Add-On Purchased ✅)

- **Add-on active** — news trading is permitted around events
- **Hard restriction still applies:** No trades opened or closed **5 minutes before OR after** any high-impact news event — this is a **hard breach** even with the add-on
- **Applies to:** Manual trades, pending orders, stop losses, and take profits
- **USD news:** ALL pairs restricted, including Gold (XAU/USD), BTC/USD, ETH/USD
- **Key events to watch:** NFP, CPI, FOMC, Fed Chair speeches — all directly affect your 3 assets
- **Rule:** Be fully flat or have SL/TP placed outside the ±5 min window before any red event

---

## 🗓️ Weekend Holding (Add-On Purchased ✅)

- **Add-on active** — positions can be held over the weekend
- **Risk reality at 1:1:** Weekend gaps at 1:1 are less destructive than leveraged positions, but still real
- **Gold:** Subject to geopolitical gap opens on Sunday
- **BTC/ETH:** Crypto trades 24/7 — weekend moves are continuous, not gapped; lower gap risk than Gold
- **Recommendation:** Only hold over weekend if trade is at least **+$50 in profit (0.5%)** with a confirmed SL set

---

## 💱 Swap-Free Account (Selected ✅)

- **No swap/rollover fees** on overnight positions — critical for 1:1 trading where holds tend to be longer
- **Benefit:** Hold BTC, ETH, and Gold overnight freely without cost erosion eating into the $800 target
- **Platform:** MTR (MatchTrader) — new trading day starts at **22:00 UTC**

---

## 📐 Position Sizing — 1:1 Trading (No Leverage)

Trading at 1:1 means your full position value is backed by capital dollar-for-dollar. No amplification, no margin risk.

| Asset | 1:1 Implication | Example for $50 risk (0.5%) |
|---|---|---|
| **BTC** (~$100,000/unit) | Micro-lots required | 0.001 BTC = ~$100 notional |
| **ETH** (~$2,500/unit) | More flexible sizing | 0.02 ETH = ~$50 notional |
| **BCH** (~$400/unit) | Very flexible sizing | 0.1 BCH = ~$40 notional |
| **Gold (XAU)** (~$3,200/oz) | Use 0.01–0.05 lot sizes | SL distance determines exact size |
| **Silver (XAG)** (~$33/oz) | Lower price, more units | SL distance determines exact size |
| **Crude Oil (WTI)** (~$75/barrel) | Moderate price, flexible | SL distance determines exact size |

> ✅ **Advantage of 1:1:** A single volatile move cannot blow the account. Drawdown is naturally contained. This is the safest approach for a prop challenge.

---

## 📈 Trading Strategy — Williams Alligator + Heiken Ashi

### Philosophy
The goal is **not** to catch every move. The goal is to take **2 high-quality trades per day** with a consistent $15–25 profit each, compounding slowly toward $800 over 3–6 months. Patience is the edge.

At $20 average profit per trade, 2 trades/day, 4 trading days/week → **~$160/week → $800 target in ~5 weeks of clean trading.** With rest days and losses factored in, 2–4 months is realistic.

---

### 🎯 Conviction Strategy

Every trade must be classified before entry. Conviction level determines your TP target and acceptable risk.

| Conviction Level | Criteria | TP Target | When to Use |
|---|---|---|---|
| **HC — High Conviction** | Trend confirmed + news aligned + chart pattern clear | **$20–$25** | All 3: strong 4H trend, clean HA, news catalyst |
| **MC — Medium Conviction** | Trend confirmed + chart pattern clear, no news | **$15–$20** | Strong 4H + clean HA, neutral news |
| **LC — Low Conviction** | Trend present but noisy or early signal | **$10–$15** | Use sparingly — consider skipping |

> **Rule:** If you cannot clearly classify a trade as HC or MC before entry — it is LC or lower. LC trades should be rare. When in doubt, skip.

---

### 🔄 Loss Recovery Strategy

When a SL is hit, do NOT increase size emotionally. Follow this structured step-down:

| Stage | Situation | Action |
|---|---|---|
| **Normal** | No recent SL hit | Trade standard size ($500–$1,000 notional) |
| **Stage 1** | 1 SL hit (lost ~$15–25) | Drop notional to **$500 max**, HC trades only |
| **Stage 2** | 2 SL hits in same day | **Stop trading for the day** — daily loss protection |
| **Next day** | After a losing day | Start with **$500 notional**, MC/HC only, rebuild slowly |

> **The doubling trap:** Never double position size to "recover" a loss. A $15 loss recovered by doubling and losing again becomes $30+ loss — compounding in the wrong direction. The recovery is done through **more winning trades at normal size**, not bigger trades.

---

### 🖥️ Pre-Session Routine (Before Every Trading Session)

1. **Check NY Stock Market open** — PST 5:30–7:00 PM (UTC 00:30–02:00) for crypto correlation
2. **Check heatmap** of your selected assets — which ones are moving with volume?
3. **Review economic calendar** — mark all red events for the session, set 30-min no-trade windows
4. **Find the dip or the trend** — identify the dominant direction on 4H before touching 15M
5. **Confirm conviction level** — HC/MC/LC before any entry attempt
6. **Set realistic expectations** — $20–$25 target today, not $100

---

### 🐊 Indicator Setup

**Full 5-Layer Confluence System — all 5 must align for a valid signal**

---

**Layer 1 — Williams Alligator (Trend Direction + Strength)**
- Jaw (Blue): 13-period SMMA, shifted 8 bars
- Teeth (Red): 8-period SMMA, shifted 5 bars
- Lips (Green): 5-period SMMA, shifted 3 bars
- Applied on: 15M and 1H entry timeframe
- Tells you: Which direction the trend is moving and how strong it is

---

**Layer 2 — Heiken Ashi Candles (Momentum Visual)**
- Replace standard candles on your chart entirely
- Applied on: 15M or 1H — no lower
- Tells you: Whether momentum is clean and sustained or hesitating

---

**Layer 3 — RSI 14 (Momentum Confirmation + Exhaustion Guard)**
- Period: 14 | Applied on: 15M or 1H (same as entry timeframe)
- **Long trades:** RSI must be above 50 and below 70
- **Short trades:** RSI must be below 50 and above 30
- RSI above 70 = overbought, do not enter long — move is likely exhausted
- RSI below 30 = oversold, do not enter short — move is likely exhausted
- Tells you: Whether momentum has room to continue or is running out of fuel

---

**Layer 4 — Volume (Real Money Confirmation)**
- Use the standard volume bar indicator on your chart
- Applied on: 15M or 1H entry timeframe
- **Rule:** The entry candle volume must be **above the 20-period average volume**
- Low volume signal = no institutional interest = unreliable regardless of pattern
- Tells you: Whether real money is behind the move or it is a fake-out

---

**Layer 5 — EMA 50 + EMA 200 (Macro Trend Bias)**
- Applied on: **4H timeframe only** — bias filter, not entry trigger
- **Bullish bias:** Price above both EMA 50 and EMA 200
- **Bearish bias:** Price below both EMA 50 and EMA 200
- **Conflicted/avoid:** Price between EMA 50 and EMA 200 — choppy zone
- Golden Cross (EMA 50 crosses above EMA 200) = strong bullish environment
- Death Cross (EMA 50 crosses below EMA 200) = strong bearish environment
- Tells you: What the macro trend environment is before you look at any entry signal

---

**Recommended Timeframe Stack**
- **Daily** → Check EMA 50/200 position once per day for macro bias
- **4H** → Confirm EMA bias + Alligator direction
- **15M or 1H** → Entry timeframe — Alligator + HA + RSI + Volume all checked here

---

### ✅ Entry Rules — Long (Buy)

All 8 conditions must be met before entering:

1. **EMA bias is bullish** — on 4H, price is above both EMA 50 and EMA 200
2. **4H Alligator agrees** — open upward, Lips above Teeth above Jaw
3. **15M/1H Alligator is awake and open upward** — all 3 lines fanning up and separated
4. **Price is above all 3 Alligator lines** — candle body not touching any line
5. **Heiken Ashi candles are solid green** — no lower wicks on recent 2–3 candles
6. **RSI is between 50 and 70** — momentum is bullish with room to run
7. **Entry candle volume is above 20-period average** — real money is participating
8. **No high-impact news within 30 minutes** — economic calendar is clear

---

### ✅ Entry Rules — Short (Sell)

All 8 conditions must be met before entering:

1. **EMA bias is bearish** — on 4H, price is below both EMA 50 and EMA 200
2. **4H Alligator agrees** — open downward, Lips below Teeth below Jaw
3. **15M/1H Alligator is awake and open downward** — all 3 lines fanning down and separated
4. **Price is below all 3 Alligator lines** — candle body not touching any line
5. **Heiken Ashi candles are solid red** — no upper wicks on recent 2–3 candles
6. **RSI is between 30 and 50** — momentum is bearish with room to run
7. **Entry candle volume is above 20-period average** — real money is participating
8. **No high-impact news within 30 minutes** — economic calendar is clear

---

### 🎯 Conviction Classification with Multi-Indicator Confluence

With 8 conditions now required, conviction is determined by **how strongly** each condition is met — not just whether it is met.

| Condition | HC Signal | MC Signal |
|---|---|---|
| EMA 50/200 | Price well above/below both, wide gap | Price just crossed, narrow gap |
| 4H Alligator | Wide separation, strong fan | Moderate separation |
| 15M Alligator | Wide separation, strong fan | Moderate separation |
| HA candles | 3+ clean candles, no wicks | 2 clean candles, minor wicks |
| RSI | 55–65 (Long) / 35–45 (Short) | 50–55 (Long) / 45–50 (Short) |
| Volume | Significantly above average | Slightly above average |

> **HC:** 5–6 conditions strongly met → TP $20–$25
> **MC:** All 8 met but moderately → TP $15–$20
> **LC:** All 8 technically met but weakly → Skip or $10–$15 max

---

### ❌ Do NOT Enter When

- Alligator lines are intertwined or flat (sleeping) — price is ranging, no trade
- Price is crossing through the Alligator lines — too late or too risky
- Heiken Ashi candles have wicks on both sides — indecision, wait
- RSI is above 70 (long) or below 30 (short) — momentum exhausted, move is likely over
- RSI is between 45–55 — no clear momentum, Alligator signal is weak
- Volume is below the 20-period average — no institutional participation, signal unreliable
- Price is between EMA 50 and EMA 200 on 4H — choppy zone, no clear macro bias
- Daily loss has hit $200 — reduce to 1 trade max for the rest of the day
- Daily loss has hit $350 — stop trading entirely for the day
- Within 30 minutes of a major news event

---

### 📵 Days & Periods to Avoid Trading Entirely

These are high-noise, low-quality environments where even valid signals fail unpredictably:

| Period | Reason | Action |
|---|---|---|
| **FOMC Decision Day** | Extreme volatility across all assets | No trades entire day |
| **NFP Friday** (1st Friday of month) | Gold, Oil, crypto all spike unpredictably | No trades from 13:00 UTC onward |
| **CPI Release Day** | USD moves violently, affects every asset | Avoid 1H before and after release |
| **Christmas week** (Dec 24–26) | Near-zero liquidity, spreads widen | No trades |
| **New Year week** (Dec 31–Jan 2) | Same as Christmas — erratic moves | No trades |
| **Major geopolitical breaking news** | Gaps and slippage destroy setups | Close platform, wait for calm |
| **Monday first 30 min** (00:30–01:00 UTC) | Weekend gap resolution, erratic opening | Wait for market to settle |

---

### 🔗 Correlation Rule — Avoid Double Exposure

Never hold two correlated assets simultaneously. It doubles your hidden risk while appearing to be two separate trades.

| If you are in… | Do NOT open… | Reason |
|---|---|---|
| **BTC** | ETH or BCH | All crypto moves together — same exposure |
| **ETH** | BTC or BCH | Same crypto market risk |
| **Gold (XAU)** | Silver (XAG) | Both are safe-haven metals, near-identical moves |
| **Silver (XAG)** | Gold (XAU) | Same as above |

> **Crude Oil** is the only asset that moves independently from the above groups. It can be traded alongside one crypto or one metal — but never both at once.

> **Rule:** One trade open at a time per correlated group. Maximum 2 open trades only if they are from different uncorrelated groups (e.g. BTC + Crude Oil).

---

### 🎯 Take Profit & Stop Loss Rules

**The anchor is always TP = $25 maximum. The RR ratio determines your SL.**

| RR Ratio | TP ($) | SL ($) |
|---|---|---|
| 1:1 | $25 | $25 |
| 1:1.5 | $25 | $16.67 |
| 1:2 | $25 | $12.50 |

- **Default TP:** $20 — use this on most trades
- **Max TP:** $25 — only when Alligator lines are strongly separated and HA candles are clean
- **Min TP:** $15 — only acceptable if RR is 1:2 (risking $7.50 to make $15)
- **SL must be placed before entry** — no exceptions, ever
- **Choose your RR before entry** based on where the natural SL level sits (Alligator jaw/teeth, recent HA swing)
- If the natural SL placement makes your dollar risk exceed $25 → **skip the trade entirely**

**How to pick RR on each trade:**
- Strong trend, clean HA, wide Alligator separation → use **1:2** (smaller SL, more upside)
- Moderate trend, some noise → use **1:1.5**
- Tight range but valid signal → use **1:1** only if TP is $20–$25

---

### 💰 Position Sizing per Trade

**Core rule:** Notional position value must not exceed **$1,000**. Size is then calculated to hit your chosen TP of $15–$25.

**Formula:**
> Position size = TP in $ ÷ Expected price move to TP
> Verify: Position size × SL distance ≤ $25

| Asset | Typical TP move (price) | Position size for $20–$25 TP | Max notional cap |
|---|---|---|---|
| **BTC** (~$100,000) | $500–$1,500 | 0.00002–0.00005 BTC | $1,000 |
| **ETH** (~$2,500) | $50–$150 | 0.0002–0.0005 ETH | $1,000 |
| **BCH** (~$400) | $8–$20 | 0.01–0.03 BCH | $1,000 |
| **Gold (XAU)** (~$3,200/oz) | $5–$15/oz | 0.02–0.05 oz | $1,000 |
| **Silver (XAG)** (~$33/oz) | $0.40–$1.00 | 0.25–0.60 oz | $1,000 |
| **Crude Oil (WTI)** (~$75/barrel) | $0.60–$1.50 | 0.15–0.40 barrels | $1,000 |

> **Example — Gold at 1:1.5 RR:**
> TP target = $20. Expected TP move = $10/oz. Position = 20 ÷ 10 = 2 oz (0.02 lot).
> SL = $20 ÷ 1.5 = $13.33 risk. SL distance = 13.33 ÷ 2 oz = $6.67/oz below entry. ✅ Under $1,000 notional.

> **If position size to hit $20 TP requires more than $1,000 notional → reduce TP to $15 or skip the trade.**

---

### 📋 Pre-Trade Checklist (Run Before Every Entry)

**Macro Bias (4H)**
- [ ] EMA 50 and EMA 200 checked — price clearly above (long) or below (short) both?
- [ ] 4H Alligator awake and aligned with EMA bias?

**Entry Signal (15M/1H)**
- [ ] 15M/1H Alligator awake and fanning in correct direction?
- [ ] Price fully above/below all 3 Alligator lines — not touching?
- [ ] Heiken Ashi candles clean — no opposing wicks on last 2–3 candles?
- [ ] RSI between 50–70 (long) or 30–50 (short)?
- [ ] Entry candle volume above 20-period average?

**Risk & Timing**
- [ ] Economic calendar checked — no news within 30 min?
- [ ] Not a blackout period (FOMC, NFP, CPI, Monday open, holidays)?
- [ ] Daily P&L checked — not at $350 loss?
- [ ] 30-minute cool-down observed since last SL hit?
- [ ] No correlated asset already open?

**Sizing & Execution**
- [ ] Current account balance tier checked — correct TP range selected?
- [ ] Conviction level classified: HC / MC / LC?
- [ ] RR ratio chosen (1:1 / 1:1.5 / 1:2) based on conviction strength?
- [ ] SL level identified at natural structure (Alligator line or HA swing)?
- [ ] SL dollar risk ≤ $25?
- [ ] TP set within tier range and notional position ≤ $1,000?

**If any box is unchecked → do not enter. Wait for the next setup.**

---

### 🗓️ Weekly Routine

| Day | Action |
|---|---|
| **Sunday** | Review economic calendar for the week. Mark all red events on BTC, ETH, Gold, Oil, Silver. Plan session times. |
| **Mon–Thu** | Active trading days. Max 2 trades/day. Journal every trade. |
| **Friday** | Optional light trading only in morning session (before 12:00 UTC). Go flat by 20:00 UTC regardless. |
| **Saturday** | Review journal. What worked? What didn't? No trading. |

---

### 🧠 Psychology & Discipline Rules

**Cool-Down Rule After an SL Hit**
- After any SL is hit — mandatory **30 minute minimum wait** before considering the next entry
- Use the time to: close the chart, review what happened, check the calendar, reset mentally
- Do not look for an immediate "recovery trade" — this is the most dangerous moment in trading

**Maximum Consecutive SL Hits**
- **2 SL hits in one day** → Stop trading for the rest of that day, no exceptions
- **3 SL hits in one week** → Stop trading for the remainder of that week
- Return only on the next session/week with reduced size and HC trades only
- This is not punishment — it is recognising that market conditions are not aligned with your setup

**Plan Drift Check**
- Every 2 weeks, ask yourself honestly:
  - Am I still following the checklist before every trade?
  - Am I still waiting for HC/MC signals only?
  - Am I entering trades I would have skipped a month ago?
  - If yes to the last one → reset to basics, re-read this document

---

### 📓 Trade Journal — Log Every Trade

Record these fields for every trade without exception:

- Date & time (UTC)
- Asset
- Direction (Long/Short)
- Account balance at entry (which tier?)
- Conviction level (HC / MC / LC)
- Entry price
- SL price & distance
- TP price & distance
- RR ratio used
- Position size (notional)
- EMA bias on 4H (bullish / bearish / conflicted)
- 4H Alligator status (awake/sleeping/transitioning)
- 15M/1H Alligator status (awake/sleeping/transitioning)
- HA candle quality (clean/wicks/mixed)
- RSI value at entry
- Volume vs average (above / below / at)
- Result: Win/Loss/BE
- P&L in $
- Notes (what you saw, what you felt, what you'd do differently)

**Review weekly:** If an asset is producing repeated SL hits over 10+ trades → stop trading that asset for 2 weeks, review your setups, and identify what signal you are misreading.

**Screenshot Rule — Mandatory**
- Take a screenshot of the chart **at entry** and **at trade close** for every single trade
- Save with filename format: `DATE_ASSET_LONG/SHORT_WIN/LOSS` (e.g. `20260516_GOLD_LONG_WIN`)
- Review screenshots on Saturday — pattern recognition comes from seeing your own trades visually, not just numbers

---

### 📅 Monthly Self-Review Checklist

Run this at the end of every month without exception:

- [ ] Am I following the pre-trade checklist before every entry?
- [ ] Am I correctly classifying HC / MC / LC before entering?
- [ ] Am I respecting the 30-minute cool-down after SL hits?
- [ ] Am I avoiding correlated assets simultaneously?
- [ ] Am I avoiding the blackout periods (FOMC, NFP, CPI)?
- [ ] Have I been entering trades I would have skipped last month?
- [ ] Is my TP/SL being set before entry every time — no changes after?
- [ ] Are my screenshots captured for every trade?
- [ ] Is my account balance tier being respected (TP adjusted per tier)?
- [ ] Am I still on track for the 5–6 month completion target?

> If more than 3 boxes are unchecked → take a full week off trading, re-read this document, and restart fresh.

---

### 📊 Progress Tracker — Phase 1

| Metric | Value |
|---|---|
| Profit target | $800 |
| Target profit per trade | $20 default, $25 max |
| Max trades per day | 2 |
| Active trading days per week | 4 |
| Estimated trades per month | 20–30 (avg 25) |
| Monthly profit target | 2–3% ($200–$300) |
| Challenge completion target | 5–6 months |

> The approach is built on **only taking valid setups**. A day with 0 trades because no setup qualified is a perfect day — not a missed opportunity. Quality of entry is everything.

**Accumulative target logic:** 75 trades × $20 avg = $1,500 = 1.5% monthly. As consistency improves, this should grow to 2–3% monthly naturally — through better setups, not bigger risk.

---

### 📊 Account Balance Tier System

Your TP target, risk level, and conviction requirement adjust automatically based on current account balance. This protects gains when ahead and preserves capital when behind.

**When account is BELOW starting balance (drawdown mode):**

| Account Balance | TP per Trade | Risk Level | Conviction Required |
|---|---|---|---|
| $9,750 – $10,000 | $15–$20 | Low–Medium | Medium (MC+) |
| $9,500 – $9,750 | $10–$15 | Low | Medium–High (MC/HC) |
| Below $9,500 | $10 max | Low | **HC only** |

**When account is ABOVE starting balance (profit mode):**

| Account Balance | TP per Trade | Risk Level | Conviction Required |
|---|---|---|---|
| $10,000 – $10,500 | $20–$25 | Medium | MC or HC |
| $10,500 – $11,000 | $15–$20 | Medium–Low | **HC only** |
| $11,000 – $11,300 | $10–$15 | Low | **HC only** |

> **Logic:** When near the profit target ($11,300), take smaller profits with the highest conviction only — protect what you've built. When in drawdown, shrink risk and wait for only the clearest setups. Same discipline applies in both directions.

> **"Same goes for vice versa"** — the system is symmetric. Gains are protected as aggressively as losses are managed.

---

## 🛡️ Personal Risk Parameters (Phase 1)

| Parameter | Official Rule | Your Operating Rule |
|---|---|---|
| Daily loss limit | 5% ($500) | **Hard stop at 3.5% ($350)** |
| Daily loss warning | — | **Reduce to 1 trade at $200 loss** |
| Max trades per day | Not specified | **2 trades maximum — no exceptions** |
| Max notional per trade | Not specified | **$1,000 position cap** |
| Single trade TP | Not specified | **$20 default, $25 absolute max, $15 min** |
| Single trade SL | Not specified | **Determined by RR chosen — max $25 risk** |
| RR ratio | Not specified | **1:1 to 1:2 — chosen per trade based on trend strength** |
| Overall drawdown | 10% ($1,000) | **Personal ceiling at 6% ($600 loss)** |
| Trade hold minimum | 2 min average | **3 min minimum per trade** |
| Ideal hold time | No max | **15 min – 4H entries, hold until TP/SL** |
| Timeframe | Not specified | **4H for direction, 15M/1H for entry** |
| News window | ±5 min hard breach | **No entry within 30 min of red event** |
| Weekend holds | Allowed (add-on) | **Only if +$20 profit with SL confirmed** |
| Leverage | Up to 1:50 available | **1:1 only — no leverage used** |

---

## 🔑 Phase 1 Key Rules Summary

1. **No trades opened/closed within 5 min of high-impact news** — hard breach
2. **Daily loss (closed + floating) must never exceed $500** — hard breach
3. **Account equity must never drop below $9,000** — hard breach
4. **Average trade duration must exceed 2 minutes** — reset penalty
5. **Minimum 3 trading days** must be completed before phase passes
6. **No third-party copy trading or account sharing** — hard breach
7. **Single IP region** — trading from multiple regions is flagged
8. **EAs allowed** but account must remain under your control at all times
9. **Goal:** Reach **$10,800 balance** (8% profit) without breaching any rule above

---

## ⏰ Trading Session Guide (BTC, ETH, Gold — MTR UTC Time)

| Asset | Best Session (UTC) | Avoid |
|---|---|---|
| **BTC** | 13:00–17:00 (NY Open) | Asian session, ±5 min around news |
| **ETH** | 07:00–12:00 (London–NY overlap) | Low volume periods |
| **BCH** | 13:00–17:00 (NY Open, follows BTC) | Asian session, low liquidity windows |
| **Gold (XAU)** | 07:00–10:00 (London Open) | ±5 min around NFP, CPI, FOMC |
| **Silver (XAG)** | 07:00–10:00 (London Open, tracks Gold) | ±5 min around USD news, more volatile than Gold |
| **Crude Oil (WTI)** | 13:00–17:00 (NY Open, peak liquidity) | EIA inventory reports (Wednesdays 14:30 UTC) ±5 min |

---

## 🖥️ MTR Platform — Order Placement SOP

Follow this exact sequence every time. Skipping steps causes errors.

1. Open MTR and verify account balance and daily P&L on dashboard
2. Check economic calendar — confirm no news within 30 minutes
3. Open asset chart → switch to Heiken Ashi candles → apply Alligator
4. Check 4H timeframe first → confirm trend direction
5. Switch to 15M or 1H → confirm entry signal
6. Run full pre-trade checklist — all boxes must be checked
7. Calculate position size before touching the order panel
8. Open new order → set direction (Buy/Sell)
9. Enter position size
10. **Set SL first** → then set TP
11. Confirm both SL and TP are visible on chart before submitting
12. Submit order
13. Take entry screenshot immediately
14. **Do not touch the trade again** — TP and SL are final, no modifications

> **TP and SL are set in stone once placed.** Mock Capital considers mid-trade modifications negatively. Place them correctly the first time or do not place the trade.

---

### 📡 Dashboard Monitoring During Open Trades

- Check dashboard **every 15 minutes** during an open trade — not more frequently
- Checking too often leads to emotional interference — trust the setup
- Only action required is if a **news event is approaching** that you missed — in that case, accept the outcome, you cannot modify
- After trade closes (TP or SL hit) → log in journal → take exit screenshot → start 30-min cool-down before next evaluation

---

- Floating loss + closed loss combo creeping past $500 in one session without noticing
- SL or TP auto-executing within 5 minutes of a news event — still a hard breach
- Scalping under 3 minutes repeatedly — drags average duration below 2 min threshold
- Holding Gold over weekends without a confirmed SL set
- Chasing the $800 target by increasing size late in the phase — stay at 0.5% per trade always

---

*Source: mockapital.com/faqs | mockapital.com/funding-programs — verified May 2026*
