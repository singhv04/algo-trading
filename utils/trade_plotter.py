import plotly.graph_objs as go


def plot_single_trade(segment_df, trade, show_indicators):
    """
    Builds an interactive plot of OHLCV data for a single trade,
    including selected indicators, entry/exit markers, trailing stop-loss,
    SL breach points, and profit/loss zone highlighting.
    """
    fig = go.Figure()

    # 1. Plot candlesticks
    fig.add_trace(go.Candlestick(
        x=segment_df['timestamp'],
        open=segment_df['open'],
        high=segment_df['high'],
        low=segment_df['low'],
        close=segment_df['close'],
        name='Price',
        increasing_line_color='green',
        decreasing_line_color='red'
    ))

    # 2. Plot selected indicators
    if 'RSI' in show_indicators and 'rsi' in segment_df.columns:
        fig.add_trace(go.Scatter(
            x=segment_df['timestamp'],
            y=segment_df['rsi'],
            name='RSI',
            mode='lines',
            line=dict(color='purple')
        ))

    if 'MACD' in show_indicators and 'macd' in segment_df.columns:
        fig.add_trace(go.Scatter(
            x=segment_df['timestamp'],
            y=segment_df['macd'],
            name='MACD',
            mode='lines',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=segment_df['timestamp'],
            y=segment_df['signal'],
            name='Signal Line',
            mode='lines',
            line=dict(color='red', dash='dot')
        ))

    if 'DMI' in show_indicators and '+DI' in segment_df.columns:
        fig.add_trace(go.Scatter(
            x=segment_df['timestamp'],
            y=segment_df['+DI'],
            name='+DI',
            mode='lines',
            line=dict(color='green')
        ))
        fig.add_trace(go.Scatter(
            x=segment_df['timestamp'],
            y=segment_df['-DI'],
            name='-DI',
            mode='lines',
            line=dict(color='red')
        ))
        fig.add_trace(go.Scatter(
            x=segment_df['timestamp'],
            y=segment_df['ADX'],
            name='ADX',
            mode='lines',
            line=dict(color='black', dash='dot')
        ))

    if 'Divergence' in show_indicators and 'divergence' in segment_df.columns:
        for _, row in segment_df.iterrows():
            if row['divergence'] == 'bullish':
                fig.add_trace(go.Scatter(
                    x=[row['timestamp']],
                    y=[row['low']],
                    mode='markers',
                    name='Bullish Div',
                    marker=dict(color='limegreen', size=8, symbol='circle')
                ))
            elif row['divergence'] == 'bearish':
                fig.add_trace(go.Scatter(
                    x=[row['timestamp']],
                    y=[row['high']],
                    mode='markers',
                    name='Bearish Div',
                    marker=dict(color='firebrick', size=8, symbol='circle')
                ))

    # 3. Entry and Exit Markers
    fig.add_trace(go.Scatter(
        x=[trade['entry_time']],
        y=[trade['entry_price']],
        mode='markers',
        name='Entry',
        marker=dict(symbol='triangle-up', color='blue', size=12)
    ))

    fig.add_trace(go.Scatter(
        x=[trade['exit_time']],
        y=[trade['exit_price']],
        mode='markers',
        name='Exit',
        marker=dict(symbol='x', color='black', size=10)
    ))

    # 4. Trailing Stop-Loss Line
    if 'stop_loss' in segment_df.columns:
        fig.add_trace(go.Scatter(
            x=segment_df['timestamp'],
            y=segment_df['stop_loss'],
            mode='lines+markers',
            name='Trailing SL',
            line=dict(color='red', dash='dash'),
            marker=dict(size=4)
        ))

        # 5. Stop-Loss Breaches
        if trade['direction'] == 'buy':
            breaches = segment_df[segment_df['close'] <= segment_df['stop_loss']]
        else:
            breaches = segment_df[segment_df['close'] >= segment_df['stop_loss']]

        fig.add_trace(go.Scatter(
            x=breaches['timestamp'],
            y=breaches['close'],
            mode='markers',
            name='SL Breach',
            marker=dict(size=10, color='black', symbol='x')
        ))

    # 6. Profit/Loss Zone
    color = 'rgba(0,200,0,0.1)' if trade['profit'] >= 0 else 'rgba(255,0,0,0.1)'
    fig.add_vrect(
        x0=trade['entry_time'],
        x1=trade['exit_time'],
        fillcolor=color,
        opacity=0.3,
        layer="below",
        line_width=0,
        annotation_text="Profit Zone" if trade['profit'] >= 0 else "Loss Zone",
        annotation_position="top left"
    )

    # 7. Vertical lines at entry and exit
    fig.add_vline(x=trade['entry_time'], line_width=1.5, line_dash="dot", line_color="blue")
    fig.add_vline(x=trade['exit_time'], line_width=1.5, line_dash="dot", line_color="black")

    # 8. Final layout settings
    fig.update_layout(
        title=f"Trade #{trade.name} | {trade['direction'].upper()} | PnL ₹{trade['profit']}",
        xaxis_title="Timestamp",
        yaxis_title="Price",
        height=650,
        xaxis=dict(tickformat="%Y-%m-%d %H:%M")
    )

    return fig
