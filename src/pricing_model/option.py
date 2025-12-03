from dataclasses import dataclass

@dataclass
class Option:
    underlying_asset_price: float
    strike_price: float
    time_to_expiration: float  # in years
    risk_free_rate: float      # annual risk-free interest rate
    volatility: float          # annual volatility of the underlying asset
    option_type: str           # 'call' or 'put'