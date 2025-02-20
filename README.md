## PieTester: Backtesting TradingView Strategies with Python

PieTester is a Python-based script designed to backtest TradingView strategies written in Pine Script.  It provides a powerful and flexible way to evaluate the performance of your Pine Script strategies using historical market data, allowing you to refine and optimize them before deploying them in live trading.

**DISCLAIMER - PLEASE NOTE,** This script is provided purely for educational purposes.  It is not intended for live trading and should not be used as the sole basis for making investment decisions.  Backtesting results are hypothetical and do not guarantee future performance.  The accuracy of this script is not guaranteed, and it may contain errors or limitations.  Use at your own risk.  The author(s) of this script are not liable for any losses incurred as a result of using this script.

**How it Works:**

PieTester simplifies the backtesting process by automating the translation and execution of your Pine Script strategies.  It operates within a single folder containing both your Pine Script strategy file and the PieTester script itself.  The script follows a streamlined process:

1. **Data Acquisition:**  PieTester fetches historical market data for a specified symbol and timeframe. This data is then stored in a local `.db` file for efficient access during the backtesting process. This local database allows for faster subsequent backtests without needing to repeatedly download data.

2. **Pine Script Translation:** The core of PieTester lies in its ability to parse and translate your Pine Script strategy.  It reads your Pine Script file and converts it into an Abstract Syntax Tree (AST).  This AST representation allows PieTester to understand the logic of your strategy.

3. **Condition and Action Mapping:**  The AST is then processed to translate the Pine Script code into a series of conditions and actions that can be executed within the Python environment. This translation involves mapping Pine Script functions and variables to their Python equivalents, ensuring accurate representation of your trading logic.

4. **Backtesting Execution:**  With the strategy translated into actionable conditions and actions, PieTester runs the backtest against the historical market data stored in the `.db` file.  It simulates trading based on the defined rules, evaluating the performance of your strategy over the chosen period.

5. **Results Generation:**  Finally, PieTester generates a `.csv` results file containing detailed information about the simulated trades. This file includes key metrics such as entry and exit points, profit/loss per trade, total profit/loss, maximum drawdown, and other relevant performance indicators.  This comprehensive output allows you to thoroughly analyze the results of your backtest.

**Key Features and Benefits:**

* **Seamless Pine Script Integration:**  Directly backtest your existing TradingView strategies without significant code modification.
* **Automated Data Handling:**  Automatically fetches and manages historical market data, simplifying the backtesting setup.
* **Efficient Backtesting Engine:**  Translates Pine Script into optimized Python code for fast and accurate backtesting.
* **Detailed Results Output:**  Provides a comprehensive `.csv` report of trade information for in-depth performance analysis.
* **Local Data Storage:** Stores downloaded market data in a `.db` file, improving efficiency for repeated backtests.
* **Easy to Use:**  Simple setup and execution within a single folder.

**Getting Started:**

1. **Install Dependencies:** PieTester relies on several Python modules.  It's highly recommended to use a `requirements.txt` file to manage these dependencies.  In your project directory, create a `requirements.txt` file listing all necessary packages (e.g., pandas, sqlite3, ast, and any other dependencies required for Pine Script parsing). Then, install the dependencies by running the following command in your terminal:

```bash
pip install -r requirements.txt
```

2. **Place Files:** Place your Pine Script strategy file, the PieTester script, and the `requirements.txt` file in the same folder.
3. **Configure Settings:**  Modify the PieTester script to specify the symbol, timeframe, and other relevant parameters.
4. **Run the Script:** Execute the PieTester script.

**Example Usage:**

```bash
python PieTester.py
```

**Output:**

A `results.csv` file will be generated in the same folder, containing the backtesting results.

**Conclusion:**

PieTester offers a user-friendly and efficient solution for backtesting TradingView strategies.  By automating the translation and execution of Pine Script code, it empowers traders to thoroughly evaluate and optimize their strategies before risking real capital.  The detailed results provided by PieTester facilitate informed decision-making and contribute to more successful trading outcomes.
