def detect_divergence(df, rsi):
    """
    Detects bullish or bearish divergence using the last 2 and 3 consecutive candles.

    Logic:
    - Bullish Divergence: Price makes lower low, RSI makes higher low
    - Bearish Divergence: Price makes higher high, RSI makes lower high

    Compares:
    - Last 2 candles: i and i-1
    - Last 3 candles: i, i-1, i-2 (trend across three)

    Parameters:
        df (pd.DataFrame): Must include 'close' column
        rsi (pd.Series): RSI values aligned with df

    Returns:
        List[str]: List of labels: 'bullish', 'bearish', or ''

    Examples:
    - Bullish (3-candle):
        close: 102, 100, 98 (falling)
        rsi:   35, 36, 38 (rising)
    - Bearish (2-candle):
        close: 110, 112 (rising)
        rsi:   70, 68 (falling)
    """
    divergence = [''] * len(df)

    for i in range(2, len(df)):
        # --- 2-candle divergence ---
        price_down_2 = df['close'][i] < df['close'][i - 1]
        rsi_up_2 = rsi[i] > rsi[i - 1]

        price_up_2 = df['close'][i] > df['close'][i - 1]
        rsi_down_2 = rsi[i] < rsi[i - 1]

        # --- 3-candle divergence ---
        price_down_3 = df['close'][i] < df['close'][i - 1] < df['close'][i - 2]
        rsi_up_3 = rsi[i] > rsi[i - 1] > rsi[i - 2]

        price_up_3 = df['close'][i] > df['close'][i - 1] > df['close'][i - 2]
        rsi_down_3 = rsi[i] < rsi[i - 1] < rsi[i - 2]

        # Check for bullish divergence
        if (price_down_2 and rsi_up_2) or (price_down_3 and rsi_up_3):
            divergence[i] = 'bullish'

        # Check for bearish divergence
        elif (price_up_2 and rsi_down_2) or (price_up_3 and rsi_down_3):
            divergence[i] = 'bearish'

    return divergence
