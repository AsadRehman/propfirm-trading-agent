# Mock Capital — Phase 1 Signal Engine

Runs every 15 minutes via GitHub Actions. Pushes trading signals to ClickUp automatically.

## Setup Instructions

### Step 1 — Add GitHub Secrets

Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret

Add these 3 secrets:

| Secret Name | Value |
|---|---|
| `TWELVE_DATA_API_KEY` | Your Twelve Data API key |
| `CLICKUP_API_KEY` | Your ClickUp API token |
| `CLICKUP_LIST_ID` | Your ClickUp list ID |

### Step 2 — Enable GitHub Actions

Go to your repo → Actions tab → Enable workflows

### Step 3 — Done

The engine runs automatically every 15 minutes.
Signals appear in your ClickUp list instantly when fired.

## Signal Output in ClickUp

```
Asset: GOLD
Direction: LONG
Current Price: 3245.80
TP: 3267.80
SL: 3234.55
Volume: Above Average
Signal Time: 2026-05-16 07:15 UTC
```

## Assets Monitored

- BTC/USD
- ETH/USD
- BCH/USD
- XAU/USD (Gold)
- XAG/USD (Silver)
- WTI/USD (Crude Oil)

## Indicators Used

- Williams Alligator (13/8/5)
- Heiken Ashi
- RSI (14)
- Volume vs 20-period average
- EMA 50 + EMA 200 (4H)

## Timeframes

- 4H → Macro bias (EMA + Alligator direction)
- 15M → Entry signal (all 8 conditions)
