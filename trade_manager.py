class TradeState:
    def __init__(self, total_capital=50000, capital_per_trade=5000):
        """
        Tracks and manages a single active trade (BUY or SHORT) using capital and position sizing.

        Attributes:
            active_trade (str): 'buy' or 'short' or None
            entry_price (float): Price at which trade was entered
            stop_loss (float): Trailing stop-loss
            position_size (float): Quantity bought (capital_per_trade / entry_price)

            total_capital (float): Starting capital
            available_capital (float): Capital currently available
            capital_per_trade (float): Max allocation per trade

            entry_time (str): Timestamp of entry (for merging into trade record)
            trades (list): Unified log of completed trades
        """
        self.active_trade = None
        self.entry_price = None
        self.stop_loss = None
        self.position_size = 0
        self.entry_time = None

        self.total_capital = total_capital
        self.available_capital = total_capital
        self.capital_per_trade = capital_per_trade

        self.trades = []  # unified trade record list

    def reset(self):
        """
        Resets current trade state after exit.
        """
        self.active_trade = None
        self.entry_price = None
        self.stop_loss = None
        self.position_size = 0
        self.entry_time = None


def update_stop_loss(current_price, state, sl_percent=0.02):
    """
    Dynamically updates the trailing stop-loss based on price movement.

    Parameters:
        current_price (float): Latest close price
        state (TradeState): Current trade state
        sl_percent (float): SL trail percentage (default = 2%)

    Returns:
        float: Updated SL

    Example (BUY):
        SL updates upward if price rises (never lowers)

    Example (SHORT):
        SL updates downward if price falls (never raises)
    """
    if state.active_trade == 'buy':
        new_sl = current_price * (1 - sl_percent)
        if new_sl > state.stop_loss:
            state.stop_loss = new_sl

    elif state.active_trade == 'short':
        new_sl = current_price * (1 + sl_percent)
        if new_sl < state.stop_loss:
            state.stop_loss = new_sl

    return state.stop_loss


def should_exit_trade(current_price, state):
    """
    Checks if SL has been hit.

    Parameters:
        current_price (float): Latest close
        state (TradeState): Current state

    Returns:
        bool: True if SL hit
    """
    if state.active_trade == 'buy' and current_price <= state.stop_loss:
        return True
    if state.active_trade == 'short' and current_price >= state.stop_loss:
        return True
    return False


def execute_entry(row, signal, state, config):
    """
    Executes entry logic: assigns trade state, updates capital, computes qty.

    Parameters:
        row (pd.Series): Candle row with 'timestamp' and 'close'
        signal (str): 'buy' or 'short'
        state (TradeState): Current trade state
        config (dict): Contains stop_loss_percent

    Modifies:
        state: Sets trade details and deducts capital
    """
    price = row['close']
    timestamp = row['timestamp']

    if state.available_capital < state.capital_per_trade:
        print(f"[{timestamp}] ❌ Skipped entry due to insufficient capital.")
        return

    # Assign trade state
    state.active_trade = signal
    state.entry_price = price
    state.stop_loss = price * (1 - config["stop_loss_percent"]) if signal == 'buy' else price * (1 + config["stop_loss_percent"])
    state.position_size = round(state.capital_per_trade / price, 4)
    state.entry_time = timestamp

    # Deduct capital
    state.available_capital -= state.capital_per_trade

    print(f"[{timestamp}] ✅ ENTER {signal.upper()} @ ₹{price:.2f} | Qty: {state.position_size}")


def execute_exit(row, state):
    """
    Finalizes trade: computes PnL, restores capital, logs unified trade dict.

    Parameters:
        row (pd.Series): Current candle with 'timestamp' and 'close'
        state (TradeState): Current trade state

    Modifies:
        - Updates available capital
        - Appends to state.trades
        - Resets state
    """
    exit_price = row['close']
    timestamp = row['timestamp']
    direction = state.active_trade
    qty = state.position_size
    entry_price = state.entry_price
    entry_time = state.entry_time

    # PnL
    profit = (exit_price - entry_price) * qty if direction == 'buy' else (entry_price - exit_price) * qty
    return_pct = (profit / (entry_price * qty)) * 100 if qty > 0 else 0

    # Restore capital
    state.available_capital += (state.capital_per_trade + profit)

    # Log full trade record
    state.trades.append({
        "entry_time": entry_time,
        "exit_time": timestamp,
        "direction": direction,
        "entry_price": round(entry_price, 2),
        "exit_price": round(exit_price, 2),
        "position_size": qty,
        "profit": round(profit, 2),
        "return_pct": round(return_pct, 2),
        "capital_left": round(state.available_capital, 2)
    })

    print(f"[{timestamp}] 🔁 EXIT {direction.upper()} @ ₹{exit_price:.2f} | PnL: ₹{profit:.2f} | Return: {return_pct:.2f}%")

    state.reset()
