
# 📈 Algorithmic Trading Bot Documentation

This documentation covers the full workflow, parameter explanations, function definitions, formulas, trailing stop-loss logic, capital tracking, and trade signal generation for a modular Python-based algorithmic trading bot using 5-minute candle data.

---

## ✅ Table of Contents

1. [System Overview](#system-overview)
2. [Workflow Summary](#workflow-summary)
3. [Configuration Parameters (`config.json`)](#configuration-parameters-configjson)
4. [Technical Indicators](#technical-indicators)
5. [Trade Logic](#trade-logic)
6. [Capital Management](#capital-management)
7. [Trailing Stop Loss Logic](#trailing-stop-loss-logic)
8. [Performance Metrics](#performance-metrics)
9. [Example Scenarios](#example-scenarios)
10. [File Outputs](#file-outputs)

---

## 🔁 System Overview

This bot takes 5-minute candle data and makes single-trade decisions based on:
- RSI (momentum)
- MACD (momentum trend)
- DMI (trend strength)
- EMA (trend smoothing)
- Divergence (price-RSI reversal signal)

Supports both:
- Long (Buy) Trades
- Short (Sell/Short) Trades

---

## 🔄 Workflow Summary

- Load config and candle data
- Calculate indicators (RSI, MACD, DMI, etc.)
- Merge indicators
- Iterate through candles:
  - If no trade: Check for buy/short signal
  - If trade active: Check stop-loss or adjust trailing SL
- Log trades, calculate metrics, save CSV/JSON/PNG

---

## ⚙️ Configuration Parameters (`config.json`)

| Parameter | Description | Example | Used In |
|----------|-------------|---------|---------|
| `rsi.period` | Lookback for RSI calc | 14 | RSI calc |
| `rsi.oversold` | RSI < this → buy | 30 | Trade signal |
| `rsi.overbought` | RSI > this → short | 70 | Trade signal |
| `ema.span` | Smoothing | 20 | Trend filter |
| `macd.fast` / `slow` / `signal` | MACD EMAs | 12, 26, 9 | MACD calc |
| `dmi.period` | Lookback | 14 | DMI calc |
| `stop_loss_percent` | Initial + trailing SL | 0.02 (2%) | SL logic |
| `min_adx_strength` | ADX confirmation | 20 | Trend filter |
| `capital.total` | Total capital in account | 50000 | Capital system |
| `capital.per_trade` | Capital per trade | 5000 | Trade size |

---

## 📊 Technical Indicators

### ✅ RSI (Relative Strength Index)

**Formula**:
```
RSI = 100 - (100 / (1 + RS)) where RS = avg_gain / avg_loss
```

**Usage**:
- RSI < 30 → Oversold → Buy
- RSI > 70 → Overbought → Short

### ✅ MACD

**Formula**:
```
MACD = EMA(fast) - EMA(slow)
Signal = EMA(MACD, signal_period)
```

**Usage**:
- MACD > Signal → Bullish
- MACD < Signal → Bearish

### ✅ DMI (Directional Movement Index)

**Includes**:
- +DI
- -DI
- ADX

**Trend confirmation**:
- +DI > -DI + ADX > 20 → Uptrend
- -DI > +DI + ADX > 20 → Downtrend

### ✅ EMA (Exponential Moving Average)

**Formula**:
```
EMA_t = Price_t × α + EMA_{t-1} × (1 - α)
where α = 2 / (span + 1)
```

---

## 🧠 Trade Logic

### Function: `should_enter_trade(...)`

```python
if rsi < oversold and macd > signal and +DI > -DI and divergence == 'bullish':
    → Buy
elif rsi > overbought and macd < signal and -DI > +DI and divergence == 'bearish':
    → Short
```

---

## 💰 Capital Management

**Settings**:
- Total capital: ₹50,000
- Per-trade capital: ₹5,000

**Logic**:
- If not enough free capital → skip signal
- On exit: add back profit/loss to available capital

---

## 📉 Trailing Stop-Loss Logic

### Function: `update_stop_loss(current_price, state, sl_percent)`

```python
if trade is BUY:
    new_sl = max(prev_sl, current_price * (1 - sl_percent))
if trade is SHORT:
    new_sl = min(prev_sl, current_price * (1 + sl_percent))
```

**SL moves in your favor but never backward**

---

## 📈 Performance Metrics

| Metric | Description |
|--------|-------------|
| Total Trades | No. of trades executed |
| Wins / Losses | Breakdown of win/loss |
| Win Rate | % profitable |
| Total Profit | ₹ gained |
| Avg Profit | Per trade gain/loss |
| Max Drawdown | Peak-to-trough % loss |
| Sharpe Ratio | Risk-adjusted return |

---

## 📘 Example Scenarios

### BUY Trade

- RSI = 25
- MACD > Signal
- +DI > -DI
- Divergence = bullish

→ Buy @ ₹100  
→ SL = ₹98  
→ Price goes to ₹105 → SL trails to ₹102.9  
→ Price falls to ₹102.5 → exit

---

### SHORT Trade

- RSI = 74
- MACD < Signal
- -DI > +DI
- Divergence = bearish

→ Short @ ₹120  
→ SL = ₹122.4  
→ Price falls to ₹115 → SL updates to ₹117.3  
→ Price rises to ₹117.5 → exit

---

## 📤 File Outputs

| File | Purpose |
|------|---------|
| `output/trade_log_TIMESTAMP.csv` | Entry/Exit per trade |
| `output/performance_log_TIMESTAMP.json` | Summary + per trade return |
| `output/trade_chart_TIMESTAMP.png` | Entry/exit chart |
| `output/calculated_metrics.csv` | Full candle data with indicators |

---
