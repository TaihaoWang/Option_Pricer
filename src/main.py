from pricing_model.option import Option
from pricing_model.black_scholes import black_scholes
from pricing_model.binomial_tree import binomial_tree
from back_tester import back_tester
from download_data import download_data

underlying_price = 100  # Current price of the underlying asset
strike_price = 100      # Strike price of the option
time_to_expiration = 1  # Time to expiration in years
risk_free_rate = 0.05   # Annual risk-free interest rate
volatility = 0.2        # Annual volatility of the underlying asset
option_type = 'call'    # Type of the option: 'call' or 'put'

option_1 = Option(
    underlying_asset_price=underlying_price,
    strike_price=strike_price,
    time_to_expiration=time_to_expiration,
    risk_free_rate=risk_free_rate,
    volatility=volatility,
    option_type=option_type
)

# Black-Scholes
bs_model = black_scholes(option=option_1)
print(f"[Black-Scholes]  {option_type} price: {bs_model.price():.4f}")

# Binomial Tree
bt_model = binomial_tree(option=option_1, steps=100)
print(f"[Binomial Tree]  {option_type} price (European): {bt_model.price():.4f}")
print(f"[Binomial Tree]  {option_type} price (American): {bt_model.price(american=True):.4f}")

# American put (early exercise premium)
put = Option(underlying_price, strike_price, time_to_expiration, risk_free_rate, volatility, 'put')
bt_put = binomial_tree(option=put, steps=100)
print(f"[Binomial Tree]  put price (European): {bt_put.price():.4f}")
print(f"[Binomial Tree]  put price (American): {bt_put.price(american=True):.4f}")

# Backtest — fetch SPY data from Yahoo Finance and run
data = download_data("sndk","2018-01-01", "2027-01-01")
data = data.set_index("Date")
bt_test = back_tester(data, option_type='call', strike_pct=1.0, time_to_expiration=1/12)
bt_test.run()
bt_test.summary()
bt_test.plot()
