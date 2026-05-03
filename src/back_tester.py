import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pricing_model.option import Option
from pricing_model.black_scholes import black_scholes
from pricing_model.binomial_tree import binomial_tree


class back_tester:
    """Backtests Black-Scholes and Binomial Tree pricing models against historical data.

    For each date in the price series, a new option is priced using rolling
    historical volatility. The actual payoff is recorded at expiration, and
    model error is measured as (model_price - actual_payoff).

    Parameters
    ----------
    data : pd.DataFrame
        Historical price data with a DatetimeIndex and a 'Close' column.
    option_type : str
        'call' or 'put'.
    strike_pct : float
        Strike as a fraction of spot price at each pricing date (1.0 = ATM).
    time_to_expiration : float
        Option lifetime in years (e.g. 1/12 ≈ one month).
    risk_free_rate : float
        Annual risk-free interest rate.
    volatility_window : int
        Rolling window (in trading days) used to estimate historical volatility.
    model : str
        Which model(s) to run: 'black_scholes', 'binomial_tree', or 'both'.
    bt_steps : int
        Number of steps for the binomial tree.
    """

    TRADING_DAYS = 252

    def __init__(
        self,
        data: pd.DataFrame,
        option_type: str = 'call',
        strike_pct: float = 1.0,
        time_to_expiration: float = 1 / 12,
        risk_free_rate: float = 0.05,
        volatility_window: int = 30,
        model: str = 'both',
        bt_steps: int = 100,
    ):
        if 'Close' not in data.columns:
            raise ValueError("data must contain a 'Close' column")
        if option_type not in ('call', 'put'):
            raise ValueError("option_type must be 'call' or 'put'")
        if model not in ('black_scholes', 'binomial_tree', 'both'):
            raise ValueError("model must be 'black_scholes', 'binomial_tree', or 'both'")

        self.data = data.copy()
        self.option_type = option_type
        self.strike_pct = strike_pct
        self.time_to_expiration = time_to_expiration
        self.risk_free_rate = risk_free_rate
        self.volatility_window = volatility_window
        self.model = model
        self.bt_steps = bt_steps
        self.results: pd.DataFrame | None = None

        # Number of trading days until expiration
        self._steps_forward = max(1, round(time_to_expiration * self.TRADING_DAYS))

    def _historical_volatility(self) -> pd.Series:
        """Annualized rolling volatility from log returns."""
        log_returns = np.log(self.data['Close'] / self.data['Close'].shift(1))
        return log_returns.rolling(self.volatility_window).std() * np.sqrt(self.TRADING_DAYS)

    def run(self) -> pd.DataFrame:
        """Run the backtest. Returns a DataFrame of per-date results."""
        vol_series = self._historical_volatility()
        rows = []

        prices = self.data['Close'].values
        dates = self.data.index

        for i in range(len(prices)):
            # Skip until we have enough history for vol estimate
            vol = vol_series.iloc[i]
            if pd.isna(vol) or vol <= 0:
                continue

            # Skip if expiration goes past the end of the data
            expiry_idx = i + self._steps_forward
            if expiry_idx >= len(prices):
                break

            S = float(prices[i])
            K = S * self.strike_pct
            S_expiry = float(prices[expiry_idx])

            if self.option_type == 'call':
                actual_payoff = max(S_expiry - K, 0)
            else:
                actual_payoff = max(K - S_expiry, 0)

            option = Option(
                underlying_asset_price=S,
                strike_price=K,
                time_to_expiration=self.time_to_expiration,
                risk_free_rate=self.risk_free_rate,
                volatility=float(vol),
                option_type=self.option_type,
            )

            row = {
                'date': dates[i],
                'expiry_date': dates[expiry_idx],
                'spot': S,
                'strike': K,
                'vol': float(vol),
                'actual_payoff': actual_payoff,
            }

            if self.model in ('black_scholes', 'both'):
                bs_price = black_scholes(option=option).price()
                row['bs_price'] = bs_price
                row['bs_error'] = bs_price - actual_payoff

            if self.model in ('binomial_tree', 'both'):
                bt_price = binomial_tree(option=option, steps=self.bt_steps).price()
                row['bt_price'] = bt_price
                row['bt_error'] = bt_price - actual_payoff

            rows.append(row)

        self.results = pd.DataFrame(rows).set_index('date')
        return self.results

    def summary(self) -> None:
        """Print performance metrics for each model."""
        if self.results is None:
            raise RuntimeError("Call run() before summary().")

        print(f"\n{'=' * 52}")
        print("Backtest Summary")
        print(f"  Option type  : {self.option_type}")
        print(f"  Strike       : {self.strike_pct * 100:.0f}% of spot (at pricing date)")
        print(f"  Expiration   : {self._steps_forward} trading days")
        print(f"  Vol window   : {self.volatility_window} days")
        print(f"  Period       : {self.results.index[0].date()} → {self.results.index[-1].date()}")
        print(f"  Observations : {len(self.results)}")

        payoffs = self.results['actual_payoff']
        print(f"\nActual payoff stats:")
        print(f"  Mean payoff      : {payoffs.mean():.4f}")
        print(f"  Expired worthless: {(payoffs == 0).mean() * 100:.1f}%")

        model_cols = [
            ('Black-Scholes', 'bs'),
            ('Binomial Tree', 'bt'),
        ]
        for label, prefix in model_cols:
            err_col = f'{prefix}_error'
            if err_col not in self.results.columns:
                continue
            errors = self.results[err_col].dropna()
            mae = errors.abs().mean()
            rmse = np.sqrt((errors ** 2).mean())
            bias = errors.mean()
            direction = 'overpriced' if bias > 0 else 'underpriced'
            print(f"\n{label}:")
            print(f"  MAE  : {mae:.4f}")
            print(f"  RMSE : {rmse:.4f}")
            print(f"  Bias : {bias:.4f} ({direction})")

        print(f"{'=' * 52}\n")

    def plot(self) -> None:
        """Plot model prices vs actual payoffs and pricing errors over time."""
        if self.results is None:
            raise RuntimeError("Call run() before plot().")

        has_bs = 'bs_price' in self.results.columns
        has_bt = 'bt_price' in self.results.columns

        fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        fig.suptitle(
            f"Option Pricer Backtest — {self.option_type.capitalize()} "
            f"({self.strike_pct * 100:.0f}% strike, {self._steps_forward}d expiry)",
            fontsize=13,
        )

        # --- Top: model prices vs actual payoff ---
        ax1 = axes[0]
        ax1.plot(self.results.index, self.results['actual_payoff'],
                 label='Actual payoff', color='black', linewidth=1.2, alpha=0.8)
        if has_bs:
            ax1.plot(self.results.index, self.results['bs_price'],
                     label='Black-Scholes price', color='steelblue', linewidth=1, alpha=0.85)
        if has_bt:
            ax1.plot(self.results.index, self.results['bt_price'],
                     label='Binomial Tree price', color='darkorange', linewidth=1,
                     linestyle='--', alpha=0.85)
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # --- Bottom: pricing error over time ---
        ax2 = axes[1]
        if has_bs:
            ax2.plot(self.results.index, self.results['bs_error'],
                     label='BS error', color='steelblue', linewidth=1, alpha=0.85)
        if has_bt:
            ax2.plot(self.results.index, self.results['bt_error'],
                     label='BT error', color='darkorange', linewidth=1,
                     linestyle='--', alpha=0.85)
        ax2.axhline(0, color='black', linewidth=0.8, linestyle=':')
        ax2.set_ylabel('Error (model − actual)')
        ax2.set_xlabel('Pricing date')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def load_csv(filepath: str, date_col: str = 'Date', close_col: str = 'Close') -> pd.DataFrame:
        """Load historical price data from a CSV file.

        The CSV must have a date column and a close price column.
        Returns a DataFrame with a DatetimeIndex and a 'Close' column.
        """
        df = pd.read_csv(filepath, parse_dates=[date_col])
        df = df.rename(columns={date_col: 'Date', close_col: 'Close'})
        df = df.set_index('Date').sort_index()
        return df[['Close']]
