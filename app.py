# ---------------------------
# File: app.py (Streamlit Dashboard)
# ---------------------------

import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.graph_objs as go
from utils.trade_segment import get_trade_segment, determine_indicators_used, resample_trade_segment
from utils.trade_plotter import plot_single_trade

# Load data
DATA_FOLDER = "output/latest"
candles_csv = os.path.join(DATA_FOLDER, "calculated_indicators.csv")
trades_csv = os.path.join(DATA_FOLDER, "executed_trades.csv")

# Read data with timezone neutral timestamps
df = pd.read_csv(candles_csv, parse_dates=['timestamp'])
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
trades = pd.read_csv(trades_csv, parse_dates=['entry_time', 'exit_time'])
trades['entry_time'] = pd.to_datetime(trades['entry_time']).dt.tz_localize(None)
trades['exit_time'] = pd.to_datetime(trades['exit_time']).dt.tz_localize(None)

# Set up Streamlit UI
st.set_page_config(layout="wide")
st.title("🔍 Trade-wise Inspector Dashboard")

# Select a trade from dropdown
trade_idx = st.selectbox("Select Trade #", range(len(trades)))
selected_trade = trades.iloc[trade_idx]
used_indicators = determine_indicators_used(selected_trade)

# Show Trade Summary
st.markdown("### Trade Summary")
st.markdown(f"**Direction:** `{selected_trade['direction'].upper()}`")
st.markdown(f"**Entry Time:** `{selected_trade['entry_time']}` @ **₹{selected_trade['entry_price']}**")
st.markdown(f"**Exit Time:** `{selected_trade['exit_time']}` @ **₹{selected_trade['exit_price']}**")
st.markdown(f"**Profit:** ₹{selected_trade['profit']} | Return: {selected_trade['return_pct']}%")
st.markdown(f"**Capital Left:** ₹{selected_trade['capital_left']}")
st.markdown(f"**Triggered by:** `{', '.join(used_indicators)}`")

# Time resampling and indicator toggles
resample_option = st.selectbox("Select Time Window", ["5min", "15min", "30min", "1H", "3H", "1D"], index=0)
all_indicators = ['RSI', 'MACD', 'DMI', 'Divergence']
selected_indicators = st.multiselect("Indicators to show:", options=all_indicators, default=used_indicators)
show_full_candles = st.checkbox("Show OHLCV candles between entry and exit", value=True)

# Segment data
segment_df = get_trade_segment(df, selected_trade)
segment_df = segment_df[segment_df['timestamp'].dt.time.between(pd.to_datetime("09:15").time(), pd.to_datetime("15:30").time())]
segment_df = segment_df[segment_df['timestamp'].dt.dayofweek < 5]
resampled_segment = resample_trade_segment(segment_df, resample_option) if show_full_candles else segment_df

# Plot base
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=resampled_segment['timestamp'],
    open=resampled_segment['open'],
    high=resampled_segment['high'],
    low=resampled_segment['low'],
    close=resampled_segment['close'],
    name='Price',
    increasing_line_color='green',
    decreasing_line_color='red'
))

# Entry and Exit markers
fig.add_trace(go.Scatter(x=[selected_trade['entry_time']], y=[selected_trade['entry_price']],
                         mode='markers', name='Entry',
                         marker=dict(symbol='triangle-up', color='blue', size=12)))
fig.add_trace(go.Scatter(x=[selected_trade['exit_time']], y=[selected_trade['exit_price']],
                         mode='markers', name='Exit',
                         marker=dict(symbol='x', color='black', size=10)))

# Trailing stop-loss line
if 'stop_loss' in segment_df.columns:
    fig.add_trace(go.Scatter(
        x=segment_df['timestamp'],
        y=segment_df['stop_loss'],
        mode='lines+markers',
        name='Trailing SL',
        line=dict(color='red', dash='dash'),
        marker=dict(size=4),
        yaxis='y1'
    ))

    # Mark SL breach points
    if selected_trade['direction'] == 'buy':
        breach_points = segment_df[segment_df['close'] <= segment_df['stop_loss']]
    else:
        breach_points = segment_df[segment_df['close'] >= segment_df['stop_loss']]

    fig.add_trace(go.Scatter(
        x=breach_points['timestamp'],
        y=breach_points['close'],
        mode='markers',
        name='SL Breach',
        marker=dict(size=10, color='black', symbol='x'),
        yaxis='y1'
    ))

# Shade profit/loss zone
entry_time = selected_trade['entry_time']
exit_time = selected_trade['exit_time']
color = 'rgba(0,200,0,0.1)' if selected_trade['profit'] >= 0 else 'rgba(255,0,0,0.1)'
fig.add_vrect(
    x0=entry_time,
    x1=exit_time,
    fillcolor=color,
    opacity=0.3,
    layer="below",
    line_width=0,
    annotation_text="Profit Zone" if selected_trade['profit'] >= 0 else "Loss Zone",
    annotation_position="top left"
)

# Entry/Exit vertical lines
fig.add_vline(x=entry_time, line_width=1.5, line_dash="dot", line_color="blue")
fig.add_vline(x=exit_time, line_width=1.5, line_dash="dot", line_color="black")

# Layout cleanup
fig.update_layout(
    title=f"Trade #{trade_idx} | {selected_trade['direction'].upper()} | PnL ₹{selected_trade['profit']}",
    xaxis_title="Timestamp",
    yaxis_title="Price",
    height=600,
    xaxis=dict(type='category', tickformat="%Y-%m-%d %H:%M")
)

# Show chart
st.plotly_chart(fig, use_container_width=True)

# Show table of values
st.markdown("### Raw OHLCV and Selected Indicator Data During Trade")
show_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
if 'RSI' in selected_indicators and 'rsi' in segment_df.columns:
    show_cols.append('rsi')
if 'MACD' in selected_indicators and 'macd' in segment_df.columns:
    show_cols.extend(['macd', 'signal'])
if 'DMI' in selected_indicators and '+DI' in segment_df.columns:
    show_cols.extend(['+DI', '-DI', 'ADX'])
if 'Divergence' in selected_indicators and 'divergence' in segment_df.columns:
    show_cols.append('divergence')
if 'stop_loss' in segment_df.columns:
    show_cols.append('stop_loss')

st.dataframe(segment_df[show_cols].reset_index(drop=True))
