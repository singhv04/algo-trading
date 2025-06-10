import pandas as pd

def calculate_ema(df, span=20):
    """
    Calculates Exponential Moving Average (EMA) on the 'close' price.

    EMA gives more weight to recent prices, which makes it more responsive
    to new information than a simple moving average (SMA).

    Parameters:
        df (pd.DataFrame): Must contain a 'close' column.
        span (int): The "smoothing" window. Higher = slower reaction.

    Returns:
        pd.Series: EMA values for the 'close' price.

    -------------------------------
    📘 Formula (internal to pandas):
        EMA_today = α * Price_today + (1 - α) * EMA_yesterday

        where α = 2 / (span + 1)
        span = 20  → α = 0.0952  → ~9.5% weight on today’s price

    -------------------------------
    🔍 Real Example:
        Let’s say prices over 3 days are: [100, 105, 110]

        - EMA_0 = 100 (starting value)
        - EMA_1 = α * 105 + (1 - α) * 100
        - EMA_2 = α * 110 + (1 - α) * EMA_1

    -------------------------------
    📈 Why EMA matters in strategy:
        - You can compare EMA of short (e.g. 12) and long (e.g. 26) spans
          to find momentum shifts.
        - EMA crossover (e.g., MACD) is a key trend-following signal.

    💡 Where It’s Used in Strategy

        In MACD:
            MACD = EMA_fast - EMA_slow

        For example:
            ema_12 = calculate_ema(df, span=12)
            ema_26 = calculate_ema(df, span=26)
            macd_line = ema_12 - ema_26
            This helps detect momentum reversals and entry signals.
             
    """
    return df['close'].ewm(span=span, adjust=False).mean()
