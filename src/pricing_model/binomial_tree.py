from dataclasses import dataclass
import numpy as np
from pricing_model.option import Option


@dataclass
class binomial_tree:
    """Cox-Ross-Rubinstein (CRR) binomial tree model.

    Supports European and American options.
    """

    option: Option
    steps: int = 100

    def price(self, american: bool = False) -> float:
        S = self.option.underlying_asset_price
        K = self.option.strike_price
        T = self.option.time_to_expiration
        r = self.option.risk_free_rate
        sigma = self.option.volatility
        n = self.steps

        dt = T / n
        u = np.exp(sigma * np.sqrt(dt))   # up factor
        d = 1 / u                          # down factor
        p = (np.exp(r * dt) - d) / (u - d)  # risk-neutral probability
        discount = np.exp(-r * dt)

        # Terminal asset prices
        asset_prices = S * u ** np.arange(n, -1, -1) * d ** np.arange(0, n + 1)

        # Terminal option payoffs
        if self.option.option_type == 'call':
            values = np.maximum(asset_prices - K, 0)
        elif self.option.option_type == 'put':
            values = np.maximum(K - asset_prices, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        # Step backwards through the tree
        for i in range(n - 1, -1, -1):
            asset_prices = S * u ** np.arange(i, -1, -1) * d ** np.arange(0, i + 1)
            values = discount * (p * values[:-1] + (1 - p) * values[1:])

            if american:
                if self.option.option_type == 'call':
                    values = np.maximum(values, asset_prices - K)
                else:
                    values = np.maximum(values, K - asset_prices)

        return float(values[0])
