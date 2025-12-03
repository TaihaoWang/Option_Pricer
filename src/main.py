from pricing_model.option import Option
from pricing_model.black_scholes import black_scholes

underlying_price = 100  # Current price of the underlying asset
strike_price = 100      # Strike price of the option
time_to_expiration = 1  # Time to expiration in years
risk_free_rate = 0.05   # Annual risk-free interest rate
volatility = 0.2        # Annual volatility of the underlying asset
option_type = 'call'    # Type of the option: 'call' or 'put

option_1 = Option(
    underlying_asset_price=underlying_price,
    strike_price=strike_price,
    time_to_expiration=time_to_expiration,
    risk_free_rate=risk_free_rate,
    volatility=volatility,
    option_type=option_type
)

bs_model = black_scholes(option=option_1)
option_price = bs_model.price()
print(f"The price of the {option_type} option is: {option_price:.2f}")