import pandas as pd
import plotly.graph_objs as go
import os


def localize_or_convert(series, timezone="Asia/Kolkata"):
    if series.dt.tz is None:
        return series.dt.tz_localize(timezone)
    else:
        return series.dt.tz_convert(timezone)


def localize_timestamp(ts, timezone="Asia/Kolkata"):
    ts = pd.to_datetime(ts)
    if ts.tzinfo is None:
        return ts.tz_localize(timezone)
    else:
        return ts.tz_convert(timezone)


def visualize_trades(
    candles_csv,
    trades_csv,
    output_path,
    indicators_to_plot=['rsi', 'macd', 'dmi', 'divergence'],
    start_time=None,
    end_time=None
):
    df = pd.read_csv(candles_csv)
    trades = pd.read_csv(trades_csv)

    # -----------------------------
    # 1. Timezone normalization
    # -----------------------------
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    trades['entry_time'] = pd.to_datetime(trades['entry_time'])
    trades['exit_time'] = pd.to_datetime(trades['exit_time'])

    df['timestamp'] = localize_or_convert(df['timestamp'])
    trades['entry_time'] = localize_or_convert(trades['entry_time'])
    trades['exit_time'] = localize_or_convert(trades['exit_time'])

    # -----------------------------
    # 2. Filter Time Range
    # -----------------------------
    if start_time:
        start_time = localize_timestamp(start_time)
        df = df[df['timestamp'] >= start_time]
        trades = trades[trades['entry_time'] >= start_time]

    if end_time:
        end_time = localize_timestamp(end_time)
        df = df[df['timestamp'] <= end_time]
        trades = trades[trades['exit_time'] <= end_time]

    # -----------------------------
    # 3. Trade Count
    # -----------------------------
    trade_count = len(trades[trades['exit_time'].notna()])
    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, "filtered_trade_count.txt"), "w") as f:
        f.write(str(trade_count))

    # -----------------------------
    # 4. Candlestick Chart
    # -----------------------------
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        increasing_line_color='green',
        decreasing_line_color='red',
        opacity=0.8
    ))

    # -----------------------------
    # 5. Plot Trailing Stop Loss Line
    # -----------------------------
    if 'stop_loss' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['stop_loss'],
            mode='lines',
            name='Trailing SL',
            line=dict(color='red', dash='dot'),
            hoverinfo='text',
            hovertext=[f"SL: ₹{sl:.2f}" if not pd.isna(sl) else None for sl in df['stop_loss']]
        ))

    # -----------------------------
    # 6. Entry / Exit Markers + SL Breaches
    # -----------------------------
    for _, trade in trades.iterrows():
        hover_text = (
            f"{trade['direction'].upper()} ENTRY<br>"
            f"RSI: {trade['rsi']}<br>"
            f"MACD: {trade['macd']} / Signal: {trade['signal_line']}<br>"
            f"+DI/-DI: {trade['+DI']} / {trade['-DI']}<br>"
            f"ADX: {trade['adx']}<br>"
            f"Divergence: {trade['divergence']}<br>"
            f"Reason: {trade['entry_reason']}"
        )

        fig.add_trace(go.Scatter(
            x=[trade['entry_time']],
            y=[trade['entry_price']],
            mode='markers',
            name=f"ENTRY - {trade['direction'].upper()}",
            marker=dict(
                color='blue' if trade['direction'] == 'buy' else 'orange',
                size=10,
                symbol='triangle-up' if trade['direction'] == 'buy' else 'triangle-down'
            ),
            hovertext=[hover_text],
            hoverinfo='text'
        ))

        fig.add_trace(go.Scatter(
            x=[trade['exit_time']],
            y=[trade['exit_price']],
            mode='markers',
            name="EXIT",
            marker=dict(color='black', size=8, symbol='x'),
            hovertext=[f"Exit ₹{trade['exit_price']} | PnL ₹{trade['profit']} ({trade['return_pct']}%)"],
            hoverinfo='text'
        ))

        # --- SL Breach Visualization ---
        segment_df = df[(df['timestamp'] >= trade['entry_time']) & (df['timestamp'] <= trade['exit_time'])]

        if trade['direction'] == 'buy':
            breach_points = segment_df[segment_df['close'] <= segment_df['stop_loss']]
        else:
            breach_points = segment_df[segment_df['close'] >= segment_df['stop_loss']]

        fig.add_trace(go.Scatter(
            x=breach_points['timestamp'],
            y=breach_points['close'],
            mode='markers',
            name="SL Breach",
            marker=dict(color='red', size=7, symbol='x'),
            hovertext=[f"SL Breach: ₹{p:.2f}" for p in breach_points['close']],
            hoverinfo='text'
        ))

    # -----------------------------
    # 7. Divergence Markers
    # -----------------------------
    if 'divergence' in indicators_to_plot:
        for _, row in df.iterrows():
            if row['divergence'] == 'bullish':
                fig.add_trace(go.Scatter(
                    x=[row['timestamp']],
                    y=[row['low']],
                    mode='markers',
                    name='Bullish Div',
                    marker=dict(color='limegreen', symbol='circle', size=6),
                    hovertext='Bullish Divergence',
                    hoverinfo='text'
                ))
            elif row['divergence'] == 'bearish':
                fig.add_trace(go.Scatter(
                    x=[row['timestamp']],
                    y=[row['high']],
                    mode='markers',
                    name='Bearish Div',
                    marker=dict(color='firebrick', symbol='circle', size=6),
                    hovertext='Bearish Divergence',
                    hoverinfo='text'
                ))

    # -----------------------------
    # 8. Layout & Chart Controls
    # -----------------------------
    fig.update_layout(
        title="Trade Chart (with Trailing Stop Loss)",
        xaxis_title="Time",
        yaxis_title="Price",
        height=800,
        xaxis_rangeslider_visible=True,
        xaxis=dict(
            type='date',
            tickformat="%H:%M",
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(step="all")
                ]
            )
        ),
        annotations=[
            dict(
                text=f"🟢 Trades in Range: {trade_count}",
                xref="paper", yref="paper",
                x=1.02, y=1,
                showarrow=False,
                font=dict(size=14, color="black"),
                align="left"
            )
        ]
    )

    # -----------------------------
    # 9. Export to HTML
    # -----------------------------
    full_html = os.path.join(output_path, "interactive_trade_chart.html")
    with open(full_html, "w") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

    print(f"✅ Chart saved: {full_html}")
