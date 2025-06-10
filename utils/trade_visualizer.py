# import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

def plot_trades(df, trade_log, save_path=None):
    """
    Plots close price along with trade entries and exits.

    Parameters:
        df (pd.DataFrame): Main price and indicator DataFrame
        trade_log (list): List of (timestamp, message) entries

    Returns:
        matplotlib plot with markers

    Example:
        Green marker at buy, red marker at sell/exit.

    """

    plt.figure(figsize=(14, 6))
    plt.plot(df['timestamp'], df['close'], label='Close Price', alpha=0.7)

    buy_points = []
    sell_points = []

    for timestamp, message in trade_log:
        price_row = df[df['timestamp'] == timestamp]
        if price_row.empty:
            continue  # Skip unmatched timestamps
        price = price_row['close'].values[0]

        if 'ENTER BUY' in message or 'EXIT SHORT' in message:
            buy_points.append((timestamp, price))
        elif 'ENTER SHORT' in message or 'EXIT BUY' in message:
            sell_points.append((timestamp, price))

    if buy_points:
        x, y = zip(*buy_points)
        plt.scatter(x, y, color='green', label='Buy/Exit Short', marker='^')
    if sell_points:
        x, y = zip(*sell_points)
        plt.scatter(x, y, color='red', label='Sell/Exit Buy', marker='v')

    plt.title("Trade Entry and Exit Points")
    plt.xlabel("Timestamp")
    plt.ylabel("Close Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    plt.close()  # Prevent GUI hang