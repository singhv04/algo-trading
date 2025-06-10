# import os
# import csv
# import json
# import pandas as pd
# from datetime import datetime

# from indicators.rsi import calculate_rsi
# from indicators.ema import calculate_ema
# from indicators.macd import calculate_macd
# from indicators.dmi import calculate_dmi
# from indicators.divergence import detect_divergence
# from trade_manager import TradeState, update_stop_loss, should_exit_trade
# from trade_manager import TradeState, update_stop_loss, should_exit_trade, execute_entry, execute_exit
# from utils.signal_logic import should_enter_trade
# from analysis.performance_metrics import calculate_performance, export_trades_to_csv

# from utils.trade_visualizer import visualize_trades


# # ----------------------------
# # Step 1: Load Configuration
# # ----------------------------
# with open("config.json") as f:
#     config = json.load(f)

# # ----------------------------
# # Step 2: Read Data
# # ----------------------------
# df = pd.read_csv("data/nifty50_5minute_data.csv")

# # Convert timestamp to datetime (if not already)
# df['timestamp'] = pd.to_datetime(df['timestamp'])

# # Optional: Filter between custom start and end time
# start_time = config.get("backtest_start_time")  # format: "YYYY-MM-DD HH:MM"
# end_time = config.get("backtest_end_time")      # format: "YYYY-MM-DD HH:MM"

# if start_time and end_time:
#     start_dt = pd.to_datetime(start_time)
#     end_dt = pd.to_datetime(end_time)
#     df = df[(df['timestamp'] >= start_dt) & (df['timestamp'] <= end_dt)]
    

# # ----------------------------
# # Step 3: Create Output Folder for This Run
# # ----------------------------
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# run_folder = f"output/backtest_run_{timestamp}"
# os.makedirs(run_folder, exist_ok=True)

# # ----------------------------
# # Step 4: Calculate Indicators
# # ----------------------------
# df['rsi'] = calculate_rsi(df, config["rsi"]["period"])
# df['ema_fast'] = calculate_ema(df, config["macd"]["fast"])
# df['ema_slow'] = calculate_ema(df, config["macd"]["slow"])
# macd = calculate_macd(df, **config["macd"])
# dmi = calculate_dmi(df, config["dmi"]["period"])
# df['divergence'] = detect_divergence(df, df['rsi'])

# # Merge MACD & DMI outputs
# df = pd.concat([df, pd.DataFrame(macd), pd.DataFrame(dmi)], axis=1)
# df.to_csv(f"{run_folder}/calculated_indicators.csv", index=False)

# # ----------------------------
# # Step 5: Initialize Trade State
# # ----------------------------
# state = TradeState(
#     total_capital=config["capital"]["total_capital"],
#     capital_per_trade=config["capital"]["per_trade"]
# )

# # ----------------------------
# # Step 6: Iterate Through Candles and Simulate Trades
# # ----------------------------
# for i in range(30, len(df)):
#     row = df.iloc[i]
#     price = row['close']

#     # If no trade active, check entry signal
#     if state.active_trade is None:
#         signal = should_enter_trade(
#             row=row,
#             rsi=row['rsi'],
#             macd_row=row,
#             dmi_row=row,
#             divergence=row['divergence'],
#             config=config
#         )
#         if signal:
#             # Check if enough capital available
#             if state.available_capital >= state.capital_per_trade:
#                 execute_entry(row, signal, state, config)
#             else:
#                 state.trades.append((row['timestamp'], "💸 Skipped: Insufficient capital"))
#     else:
#         # If in trade, check if SL hit
#         if should_exit_trade(price, state):
#             execute_exit(row, state)
#         else:
#             update_stop_loss(price, state, config["stop_loss_percent"])

# # ----------------------------
# # Step 7: Save Logs
# # ----------------------------
# # Separate full, complete, and incomplete trades

# full_logs = []
# incomplete_trades = []

# for trade in state.trades:
#     if all(k in trade for k in ["entry_time", "exit_time", "entry_price", "exit_price"]):
#         full_logs.append(trade)
#     else:
#         incomplete_trades.append(trade)

# # --- Save readable trade log to TXT ---
# log_path = f"{run_folder}/trade_log.txt"
# with open(log_path, "w") as f:
#     f.write("--- TRADE LOG ---\n")
#     for trade in full_logs:
#         f.write(
#             f"{trade['entry_time']} → {trade['exit_time']} | "
#             f"{trade['direction'].upper()} | Entry: ₹{trade['entry_price']} | "
#             f"Exit: ₹{trade['exit_price']} | PnL: ₹{trade['profit']} | "
#             f"Return: {trade['return_pct']}% | Capital Left: ₹{trade['capital_left']}\n"
#         )

# # --- Save incomplete trades if any ---
# if incomplete_trades:
#     incomplete_path = f"{run_folder}/incomplete_trades.txt"
#     with open(incomplete_path, "w") as f:
#         f.write("--- INCOMPLETE TRADES ---\n")
#         for trade in incomplete_trades:
#             f.write(f"{trade}\n")  # Raw dictionary output

# # --- Save full trades to CSV ---
# csv_file = f"{run_folder}/executed_trades.csv"
# with open(csv_file, mode='w', newline='') as file:

#     writer = csv.DictWriter(file, fieldnames = [
#         "entry_time", "exit_time", "direction",
#         "entry_price", "exit_price", "position_size",
#         "rsi", "macd", "signal_line", "+DI", "-DI", "adx", "divergence", "entry_reason",
#         "profit", "return_pct", "capital_left"
#     ])

#     writer.writeheader()
#     writer.writerows(full_logs)

# # ----------------------------
# # Step 8: Show Performance
# # ----------------------------
# metrics = calculate_performance(full_logs)
# print("\n--- STRATEGY PERFORMANCE ---")
# for k, v in metrics.items():
#     print(f"{k}: {v}")

# # Save metrics to JSON for dashboard
# summary = {
#     "summary_metrics": metrics,
#     "run_timestamp": timestamp,
#     "capital_used": config["capital"],
# }
# with open(f"{run_folder}/performance_summary.json", "w") as f:
#     json.dump(summary, f, indent=4)

# print(f"\n✅ Logs saved in: {run_folder}")

# print("visualizations...")
# visualize_trades(
#     candles_csv=f"{run_folder}/calculated_indicators.csv",
#     trades_csv=f"{run_folder}/executed_trades.csv",
#     output_path=run_folder,
#     indicators_to_plot=['rsi', 'macd', 'dmi', 'divergence'],
#     start_time=start_time,
#     end_time=end_time
# )

# # Make this run available for frontend
# import shutil
# shutil.rmtree("output/latest", ignore_errors=True)
# shutil.copytree(run_folder, "output/latest")

# print(f"\n📈 You can now run `python app.py` and visit http://localhost:5000 to explore the chart interactively.")


import os
import csv
import json
import pandas as pd
from datetime import datetime
import shutil

# --- Custom Modules ---
from indicators.rsi import calculate_rsi
from indicators.ema import calculate_ema
from indicators.macd import calculate_macd
from indicators.dmi import calculate_dmi
from indicators.divergence import detect_divergence
from trade_manager import (
    TradeState, update_stop_loss, should_exit_trade,
    execute_entry, execute_exit
)
from utils.signal_logic import should_enter_trade
from analysis.performance_metrics import calculate_performance, export_trades_to_csv
from utils.trade_visualizer import visualize_trades

# ----------------------------
# Step 1: Load Backtest Configuration
# ----------------------------
with open("config.json") as f:
    config = json.load(f)

# ----------------------------
# Step 2: Load Historical OHLCV Data
# ----------------------------
df = pd.read_csv("data/nifty50_5minute_data.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Optional: Trim date range for backtest
start_time = config.get("backtest_start_time")
end_time = config.get("backtest_end_time")

if start_time and end_time:
    start_dt = pd.to_datetime(start_time)
    end_dt = pd.to_datetime(end_time)
    df = df[(df['timestamp'] >= start_dt) & (df['timestamp'] <= end_dt)]

# ----------------------------
# Step 3: Create Output Folder
# ----------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_folder = f"output/backtest_run_{timestamp}"
os.makedirs(run_folder, exist_ok=True)

# ----------------------------
# Step 4: Compute Technical Indicators
# ----------------------------
df['rsi'] = calculate_rsi(df, config["rsi"]["period"])
df['ema_fast'] = calculate_ema(df, config["macd"]["fast"])
df['ema_slow'] = calculate_ema(df, config["macd"]["slow"])
macd = calculate_macd(df, **config["macd"])
dmi = calculate_dmi(df, config["dmi"]["period"])
df['divergence'] = detect_divergence(df, df['rsi'])

# Combine all outputs into DataFrame
df = pd.concat([df, pd.DataFrame(macd), pd.DataFrame(dmi)], axis=1)

# Initialize column to log SL trail during active trades
df['stop_loss'] = None

# ----------------------------
# Step 5: Initialize Trade Manager
# ----------------------------
state = TradeState(
    total_capital=config["capital"]["total_capital"],
    capital_per_trade=config["capital"]["per_trade"]
)

# ----------------------------
# Step 6: Iterate Candles to Simulate Strategy
# ----------------------------
for i in range(30, len(df)):  # start after warm-up period
    row = df.iloc[i]
    price = row['close']

    if state.active_trade is None:
        # Check if strategy wants to enter new trade
        signal = should_enter_trade(
            row=row,
            rsi=row['rsi'],
            macd_row=row,
            dmi_row=row,
            divergence=row['divergence'],
            config=config
        )
        if signal:
            if state.available_capital >= state.capital_per_trade:
                execute_entry(row, signal, state, config)
            else:
                state.trades.append((row['timestamp'], "💸 Skipped: Insufficient capital"))

    else:
        # Check for SL hit or update SL trail
        if should_exit_trade(price, state):
            execute_exit(row, state)
        else:
            update_stop_loss(price, state, config["stop_loss_percent"])
            df.at[i, 'stop_loss'] = state.stop_loss  # ✅ Log latest SL to visualize later

# ----------------------------
# Step 7: Save Trade Logs
# ----------------------------

# Separate valid trades from incomplete entries
full_logs = []
incomplete_trades = []

for trade in state.trades:
    if isinstance(trade, dict) and all(k in trade for k in ["entry_time", "exit_time", "entry_price", "exit_price"]):
        full_logs.append(trade)
    else:
        incomplete_trades.append(trade)

# Save enriched OHLCV data with indicators and SL
df.to_csv(f"{run_folder}/calculated_indicators.csv", index=False)

# Save trade log (readable)
with open(f"{run_folder}/trade_log.txt", "w") as f:
    f.write("--- TRADE LOG ---\n")
    for trade in full_logs:
        f.write(
            f"{trade['entry_time']} → {trade['exit_time']} | "
            f"{trade['direction'].upper()} | Entry: ₹{trade['entry_price']} | "
            f"Exit: ₹{trade['exit_price']} | PnL: ₹{trade['profit']} | "
            f"Return: {trade['return_pct']}% | Capital Left: ₹{trade['capital_left']}\n"
        )

# Save incomplete trades separately
if incomplete_trades:
    with open(f"{run_folder}/incomplete_trades.txt", "w") as f:
        f.write("--- INCOMPLETE TRADES ---\n")
        for trade in incomplete_trades:
            f.write(f"{trade}\n")

# Export complete trades to CSV
csv_file = f"{run_folder}/executed_trades.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=[
        "entry_time", "exit_time", "direction",
        "entry_price", "exit_price", "position_size",
        "rsi", "macd", "signal_line", "+DI", "-DI", "adx", "divergence", "entry_reason",
        "profit", "return_pct", "capital_left", "entry_sl"
    ])
    writer.writeheader()
    writer.writerows(full_logs)

# ----------------------------
# Step 8: Print Performance Summary
# ----------------------------
metrics = calculate_performance(full_logs)
print("\n--- STRATEGY PERFORMANCE ---")
for k, v in metrics.items():
    print(f"{k}: {v}")

with open(f"{run_folder}/performance_summary.json", "w") as f:
    json.dump({
        "summary_metrics": metrics,
        "run_timestamp": timestamp,
        "capital_used": config["capital"]
    }, f, indent=4)

# ----------------------------
# Step 9: Generate Interactive Trade Chart
# ----------------------------
print("\n📊 Generating visualization...")
visualize_trades(
    candles_csv=f"{run_folder}/calculated_indicators.csv",
    trades_csv=f"{run_folder}/executed_trades.csv",
    output_path=run_folder,
    indicators_to_plot=['rsi', 'macd', 'dmi', 'divergence'],
    start_time=start_time,
    end_time=end_time
)

# ----------------------------
# Step 10: Prepare Frontend Output
# ----------------------------
shutil.rmtree("output/latest", ignore_errors=True)
shutil.copytree(run_folder, "output/latest")

print(f"\n✅ Run complete. Visit 👉 http://localhost:5000 to view interactive chart.")
