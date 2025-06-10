import csv
import numpy as np
from typing import List, Dict


def calculate_performance(trades: List[Dict]) -> Dict[str, float]:
    """
    Calculates overall performance metrics from completed trades.

    Parameters:
        trades (List[Dict]): Each trade is a dictionary with:
            {
                "entry_time": str,
                "exit_time": str,
                "direction": "buy" or "short",
                "entry_price": float,
                "exit_price": float,
                "position_size": float,
                "profit": float,
                "return_pct": float,
                "capital_left": float
            }

    Returns:
        Dict[str, float]: Summary metrics for dashboard or report.

    Metrics Calculated:
    - total_trades: Number of completed trades
    - total_profit: Net total profit
    - avg_profit: Average profit per trade
    - win_rate_percent: Percentage of winning trades
    - max_drawdown_percent: Max drop from peak capital
    - sharpe_ratio: Risk-adjusted return (daily approx, 252 periods)

    Example:
        5 trades: [100, 102, 105, 103, 106]
        Max drawdown = (105 - 103) / 105 = 1.9%
        Sharpe = mean(returns) / std(returns) * sqrt(252)
    """
    if not trades:
        return {}

    total_profit = sum(t['profit'] for t in trades)
    avg_profit = total_profit / len(trades)

    wins = [t for t in trades if t['profit'] > 0]
    win_rate = (len(wins) / len(trades)) * 100

    # Capital curve for drawdown/sharpe
    capital_series = [100000] + [t["capital_left"] for t in trades]
    drawdowns = []
    peak = capital_series[0]
    for val in capital_series:
        if val > peak:
            peak = val
        dd = (peak - val) / peak
        drawdowns.append(dd)
    max_drawdown = max(drawdowns) * 100

    # Sharpe ratio based on capital changes
    returns = np.diff(capital_series)
    sharpe_ratio = 0
    if len(returns) > 1 and np.std(returns) != 0:
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)

    return {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(trades) - len(wins),
        "win_rate_percent": round(win_rate, 2),
        "total_profit": round(total_profit, 2),
        "avg_profit": round(avg_profit, 2),
        "max_drawdown_percent": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe_ratio, 2)
    }


def export_trades_to_csv(trades: List[Dict], filename: str = "output/trade_log.csv") -> None:
    """
    Exports all completed trades to a structured CSV file.

    Parameters:
        trades (List[Dict]): List of structured trade dictionaries
        filename (str): CSV file path

    Output Columns:
        entry_time, direction, entry_price, exit_time,
        exit_price, position_size, profit, return_percent, capital_left

    Example Row:
        "2025-06-08 10:30", "buy", 100.0, "2025-06-08 11:10", 105.0, 50.0, 250.0, 5.0, 50250.0
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "entry_time", "direction", "entry_price", "exit_time",
            "exit_price", "position_size", "profit", "return_percent", "capital_left"
        ])

        for trade in trades:
            writer.writerow([
                trade["entry_time"],
                trade["direction"],
                round(trade["entry_price"], 2),
                trade["exit_time"],
                round(trade["exit_price"], 2),
                round(trade["position_size"], 2),
                round(trade["profit"], 2),
                round(trade["return_pct"], 2),
                round(trade["capital_left"], 2)
            ])
