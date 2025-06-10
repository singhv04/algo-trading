import pandas as pd

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI) on the 'close' prices.

    RSI measures **momentum** of price movements — i.e., how fast and how much the price
    is changing. It helps detect **overbought** or **oversold** conditions.

    -------------------------------
    Parameters:
        df (pd.DataFrame): Must contain a 'close' column
        period (int): Number of candles to use in RSI smoothing (default = 14)

    Returns:
        pd.Series: RSI values, ranging between 0 and 100

    -------------------------------
    📘 RSI Formula:

        1. Gain = max(current_close - previous_close, 0)
           Loss = max(previous_close - current_close, 0)

        2. Avg Gain = rolling mean of gains over N periods
           Avg Loss = rolling mean of losses over N periods

        3. RS = Avg Gain / Avg Loss

        4. RSI = 100 - (100 / (1 + RS))

    -------------------------------
    🔍 Example:
        - Close prices = [100, 102, 101, 104, 106]
        - Gains = [2, 0, 3, 2]
        - Losses = [0, 1, 0, 0]
        - Avg Gain = mean of [2, 0, 3, 2]
        - Avg Loss = mean of [0, 1, 0, 0]
        → Compute RSI using formula

    -------------------------------
    💡 Strategy Usage:
        - RSI < 30 → asset is **oversold** → possible BUY signal
        - RSI > 70 → asset is **overbought** → possible SHORT signal
    """
    
    # Step 1: Calculate price differences (current - previous)
    delta = df['close'].diff()

    # Step 2: Separate upward and downward movements
    gain = delta.where(delta > 0, 0)  # only positive changes
    loss = -delta.where(delta < 0, 0)  # only negative changes (as positive numbers)

    # Step 3: Calculate average gain and average loss using rolling window
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Step 4: Calculate Relative Strength (RS)
    rs = avg_gain / (avg_loss + 1e-10)  # add small value to avoid divide-by-zero

    # Step 5: Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi
