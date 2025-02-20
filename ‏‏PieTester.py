"""
Crypto Trading Strategy Backtester using pynescript
----------------------------------------------------
This script:
  - Fetches historical market data via CCXT (using Binance as the example exchange)
  - Syncs the market data to a SQLite database (one file per symbol/timeframe)
  - Parses a PineScript strategy file using pynescript to generate an AST
  - Evaluates the strategy on historical OHLCV data (using a dummy evaluator)
  - Generates an Excel report with a trade summary and detailed trade orders

For more details on pynescript usage, see:
https://pynescript.readthedocs.io/en/latest/usage.html
"""

import os
import datetime
import sqlite3
import pandas as pd
import ccxt

# Import pynescript functions for parsing and un-parsing
from pynescript.ast import parse, dump, unparse

# ==============================
# CONFIGURATION VARIABLES
# ==============================

DAYS_BACK = 30  # Number of days to look back for historical data
TIMEFRAME = "3m"  # Timeframe for OHLCV data.
# Acceptable values (in CCXT/binance): "1m", "3m", "5m", "15m", "30m",
# "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M".
SYMBOL = "BTC/USDT"  # Coin symbol (e.g. "BTC/USDT")
PINE_STRATEGY_FILE = "Supertrend.pine"  # PineScript strategy file to parse
COMMISSION_RATE = 0.001  # Commission rate per trade
OUTPUT_EXCEL_FILE = PINE_STRATEGY_FILE + "-backtest_results.xlsx"
DB_FOLDER = "./db"  # Folder to store the SQLite DB files

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# ==============================
# PINE SCRIPT PARSING
# ==============================


def load_and_parse_strategy(filename):
    """
    Load the PineScript file and parse it into an AST using pynescript.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Strategy file '{filename}' not found.")
    with open(filename, "r") as f:
        script_source = f.read()
    # Parse the script to get the AST
    tree = parse(script_source)
    print("AST dump:")
    print(dump(tree, indent=2))
    # (Optionally, unparse back to verify the code)
    print("Unparsed strategy:")
    print(unparse(tree))
    return tree


# ==============================
# DUMMY STRATEGY EVALUATOR
# ==============================


def evaluate_strategy_on_bar(ast_tree, current_bar, previous_bar):
    """
    Dummy evaluator that uses the parsed PineScript AST.

    In a full implementation you would traverse the AST and convert PineScript
    conditions into Python expressions. For this example, we simply print the
    unparsed code (for debugging) and use a simple rule:
      - If current close > previous close, return "enter_long"
      - Otherwise, return "exit"
    """
    # For demonstration, print the unparsed strategy (this is static)
    strategy_code = unparse(ast_tree)
    # (In practice, you would compile and execute parts of the AST)
    # Dummy signal: if the close increased, signal long entry; else, signal exit.
    if current_bar["Close"] > previous_bar["Close"]:
        return "enter_long"
    else:
        return "exit"


# ==============================
# DATA FETCHING (using CCXT)
# ==============================


def fetch_historical_data_ccxt(symbol, timeframe, days_back):
    """
    Fetch historical OHLCV data from Binance via CCXT and cache to CSV.
    """
    print(f"Fetching historical data for {symbol}...")
    exchange = ccxt.binance({"enableRateLimit": True})
    timeframe_ms = exchange.parse_timeframe(timeframe) * 1000
    since = exchange.milliseconds() - days_back * 24 * 3600 * 1000
    all_ohlcv = []
    while True:
        ohlcv = exchange.fetch_ohlcv(
            symbol, timeframe=timeframe, since=since, limit=1000
        )
        if not ohlcv:
            break
        all_ohlcv.extend(ohlcv)
        since = ohlcv[-1][0] + timeframe_ms
        if len(ohlcv) < 1000:
            break
    df = pd.DataFrame(
        all_ohlcv, columns=["Datetime", "Open", "High", "Low", "Close", "Volume"]
    )
    df["Datetime"] = pd.to_datetime(df["Datetime"], unit="ms")
    df.set_index("Datetime", inplace=True)
    csv_file = f"{SYMBOL.replace('/', '-')}_{TIMEFRAME}.csv"
    df.to_csv(csv_file)
    print(f"Historical data saved to {csv_file}")
    return df


# ==============================
# DATABASE SYNC
# ==============================


def sync_data_to_db(symbol, timeframe, df):
    """
    Save market data to a SQLite database (one file per symbol/timeframe).
    """
    db_file = os.path.join(DB_FOLDER, f"{symbol.replace('/', '-')}_{timeframe}.db")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS market_data (
            Datetime TEXT PRIMARY KEY,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Volume REAL
        )
    """
    )
    for dt, row in df.iterrows():
        c.execute(
            """
            INSERT OR REPLACE INTO market_data (Datetime, Open, High, Low, Close, Volume)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                dt.strftime("%Y-%m-%d %H:%M:%S"),
                row["Open"],
                row["High"],
                row["Low"],
                row["Close"],
                row["Volume"],
            ),
        )
    conn.commit()
    conn.close()
    print(f"Market data synced to database: {db_file}")


# ==============================
# BACKTESTING SIMULATION
# ==============================


def backtest(ast_tree, df):
    """
    Run the backtest by evaluating the strategy on each bar.
    This simplistic loop calls the evaluator for each bar and records dummy trades.
    """
    trades = []
    position = None
    cash = 10000.0  # starting capital

    # Loop over the data from the second bar onward
    for i in range(1, len(df)):
        current = df.iloc[i]
        previous = df.iloc[i - 1]
        decision = evaluate_strategy_on_bar(ast_tree, current, previous)

        if decision == "enter_long" and position is None:
            # Enter a long position
            position = {"entry_time": current.name, "entry_price": current["Close"]}
            trades.append(
                {
                    "Trade": "Long Entry",
                    "Time": current.name,
                    "Price": current["Close"],
                    "Comment": "Entered long",
                }
            )
            cash -= current["Close"]
        elif decision == "exit" and position is not None:
            # Exit the position
            exit_price = current["Close"]
            profit = exit_price - position["entry_price"]
            trades.append(
                {
                    "Trade": "Exit",
                    "Time": current.name,
                    "Price": exit_price,
                    "Profit": profit,
                    "Comment": "Exited position",
                }
            )
            cash += exit_price
            position = None

    print(f"Final cash: ${cash:.2f}")
    return trades


# ==============================
# REPORT GENERATION
# ==============================


def generate_report(trades, df):
    summary_data = {"Total Trades": [len(trades)]}
    summary_df = pd.DataFrame(summary_data)
    orders_df = pd.DataFrame(trades)
    with pd.ExcelWriter(OUTPUT_EXCEL_FILE) as writer:
        summary_df.to_excel(writer, sheet_name="Trade Summary", index=False)
        orders_df.to_excel(writer, sheet_name="Trade Orders", index=False)
    print(f"Report generated: {OUTPUT_EXCEL_FILE}")


# ==============================
# MAIN FUNCTION
# ==============================


def main():
    # Parse the PineScript strategy using pynescript
    ast_tree = load_and_parse_strategy(PINE_STRATEGY_FILE)

    # Fetch historical data and sync to database
    df = fetch_historical_data_ccxt(SYMBOL, TIMEFRAME, DAYS_BACK)
    sync_data_to_db(SYMBOL, TIMEFRAME, df)

    # Run the backtest using the evaluated strategy
    trades = backtest(ast_tree, df)

    # Generate an Excel report with the results
    generate_report(trades, df)


if __name__ == "__main__":
    main()
