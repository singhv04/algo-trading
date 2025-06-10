🧾 config.json

{
  "rsi": {
    "period": 14,
    "oversold": 30,
    "overbought": 70
  },
  "ema": {
    "span": 20
  },
  "macd": {
    "fast": 12,
    "slow": 26,
    "signal": 9
  },
  "dmi": {
    "period": 14
  },
  "stop_loss_percent": 0.02,
  "min_adx_strength": 20
}
🔹 rsi
"rsi": {
  "period": 14,
  "oversold": 30,
  "overbought": 70
}
What it does:

Calculates the Relative Strength Index, a momentum oscillator between 0–100.
It tells you how overbought/oversold an asset is.
Parameters:

period: Number of candles for RSI calculation. Common default is 14.
oversold: If RSI falls below this, it's considered oversold → potential Buy signal.
overbought: If RSI rises above this, it's considered overbought → potential Short signal.
Examples:

RSI = 25 → very oversold → may bounce up → consider buy
RSI = 75 → very overbought → may pull back → consider short
🔹 ema
"ema": {
  "span": 20
}
What it does:

Calculates Exponential Moving Average, a trend-following indicator.
Parameter:

span: How many candles to smooth over. Smaller values → faster EMA.
Examples:

span: 9 → very responsive to price changes, fast trend shifts
span: 50 → slow EMA, better for long-term trend detection
🔹 macd
"macd": {
  "fast": 12,
  "slow": 26,
  "signal": 9
}
What it does:

MACD = difference between 12-EMA and 26-EMA
Signal line = 9-period EMA of MACD
Histogram = MACD − Signal
Parameters:

fast: Short-term EMA (default 12)
slow: Long-term EMA (default 26)
signal: EMA of MACD line (default 9)
Interpretation:

MACD > Signal → momentum rising → bullish
MACD < Signal → momentum falling → bearish
🔹 dmi
"dmi": {
  "period": 14
}
What it does:

Computes Directional Movement Index (DMI) → shows trend direction & strength
Components:

+DI: positive movement
-DI: negative movement
ADX: trend strength
Parameter:

period: smoothing window for ADX (commonly 14)
Use case:

+DI > -DI → uptrend strength
ADX > 20 → trend strong enough to trade
🔹 stop_loss_percent
"stop_loss_percent": 0.02
What it does:

Defines trailing stop-loss distance in percentage (2% default)
Example:

If you buy at ₹100, stop-loss starts at ₹98
If price rises to ₹104, stop-loss updates to ₹102
If price drops below SL → trade exits
🔹 min_adx_strength
"min_adx_strength": 20
What it does:

Ensures a trade is taken only when there's a strong trend
Why needed:

Prevents false signals in sideways market
Interpretation:

ADX < 20 → avoid trading → market too weak
ADX > 20 or 25 → ok to trade → market trending