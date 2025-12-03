from dataclasses import dataclass
import numpy as np
from scipy.stats import norm
from pricing_model.option import Option

@dataclass
class black_scholes:

    option: Option  # Instance of the Option dataclass

    def d1(self) -> float:
        S = self.option.underlying_asset_price  # Current price of the underlying asset
        K = self.option.strike_price            # Strike price of the option
        T = self.option.time_to_expiration      # Time to expiration in years
        r = self.option.risk_free_rate          # Risk-free interest rate
        sigma = self.option.volatility          # Volatility of the underlying asset
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    def d2(self) -> float:
        return self.d1() - self.option.volatility * np.sqrt(self.option.time_to_expiration)

    def price(self) -> float:
        S = self.option.underlying_asset_price
        K = self.option.strike_price
        T = self.option.time_to_expiration
        r = self.option.risk_free_rate
        sigma = self.option.volatility

        d1 = self.d1()
        d2 = self.d2()

        if self.option.option_type == 'call':
            price = (S * norm.cdf(d1)) - (K * np.exp(-r * T) * norm.cdf(d2))
        elif self.option.option_type == 'put':
            price = (K * np.exp(-r * T) * norm.cdf(-d2)) - (S * norm.cdf(-d1))
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        return price