# Option Pricer

A Python library for pricing financial options using analytical and numerical models.

## Models

| Model | Option Types | Early Exercise |
|-------|-------------|----------------|
| Black-Scholes | European call & put | No |
| Binomial Tree (CRR) | European & American call & put | Yes |

## Project Structure

```
Option_Pricer/
├── src/
│   ├── main.py                        # Example usage
│   ├── back_tester.py                 # Backtesting engine
│   ├── tests/
│   │   ├── test_black_scholes.py
│   │   └── test_binomial_tree.py
│   └── pricing_model/
│       ├── __init__.py                # Package exports
│       ├── option.py                  # Option dataclass
│       ├── black_scholes.py           # Black-Scholes model
│       └── binomial_tree.py           # CRR binomial tree model
├── requirements.txt
└── README.md
```

## Setup

```powershell
python -m venv .pricer_env
.\.pricer_env\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage

```python
from pricing_model import Option, black_scholes, binomial_tree

option = Option(
    underlying_asset_price=100,   # Current price of the underlying asset
    strike_price=100,             # Strike price
    time_to_expiration=1,         # Time to expiration in years
    risk_free_rate=0.05,          # Annual risk-free interest rate
    volatility=0.2,               # Annual volatility
    option_type='call'            # 'call' or 'put'
)
```

### Black-Scholes

```python
bs = black_scholes(option=option)
print(bs.price())   # 10.45
```

### Binomial Tree

```python
bt = binomial_tree(option=option, steps=100)
print(bt.price())                # European call: 10.43
print(bt.price(american=True))   # American call: 10.43
```

> **Note:** For call options on non-dividend-paying assets, American and European prices are equal.
> The difference appears for American puts, where early exercise can be optimal.

```python
put = Option(100, 100, 1, 0.05, 0.2, 'put')
bt_put = binomial_tree(option=put, steps=200)
print(bt_put.price())                # European put: 5.57
print(bt_put.price(american=True))   # American put: 6.09  (higher due to early exercise)
```

Run the example:

```bash
cd src
python main.py
```

### Backtester

Tests how well the pricing models predict actual option payoffs on historical data.
For each date, it prices a fresh option using rolling historical volatility, then
looks forward to the expiration date to record what the option actually paid out.

```python
from back_tester import back_tester

# Load historical price data (CSV with Date and Close columns)
data = back_tester.load_csv('data/SPY.csv')

bt = back_tester(
    data=data,
    option_type='call',
    strike_pct=1.0,           # ATM (strike = spot at pricing date)
    time_to_expiration=1/12,  # 1-month options
    risk_free_rate=0.05,
    volatility_window=30,     # 30-day rolling historical vol
    model='both',             # run Black-Scholes and Binomial Tree
    bt_steps=100,
)

bt.run()
bt.summary()
bt.plot()
```

**Example output:**

```
====================================================
Backtest Summary
  Option type  : call
  Strike       : 100% of spot (at pricing date)
  Expiration   : 21 trading days
  Vol window   : 30 days
  Period       : 2020-01-02 → 2024-12-31
  Observations : 1208

Actual payoff stats:
  Mean payoff      : 3.2147
  Expired worthless: 43.2%

Black-Scholes:
  MAE  : 1.8432
  RMSE : 2.6701
  Bias : 0.4123 (overpriced)

Binomial Tree:
  MAE  : 1.8519
  RMSE : 2.6788
  Bias : 0.4201 (overpriced)
====================================================
```

**CSV format expected:**

```
Date,Open,High,Low,Close,Volume
2020-01-02,324.66,325.88,322.53,324.87,73610900
2020-01-03,321.16,323.64,320.16,322.01,82228100
...
```

The backtester only requires `Date` and `Close` columns. You can download historical data
from [Yahoo Finance](https://finance.yahoo.com) → search ticker → Historical Data → Download.

## Model Details

### Black-Scholes

Closed-form analytical solution for European options.

**d1** = [ ln(S/K) + (r + σ²/2) · T ] / (σ · √T)

**d2** = d1 − σ · √T

**Call** = S · N(d1) − K · e^(−rT) · N(d2)

**Put** = K · e^(−rT) · N(−d2) − S · N(−d1)

### Binomial Tree (CRR)

Numerical model that builds a discrete price tree over `n` time steps. At each node, the asset can move up by factor `u` or down by `d = 1/u`. Option value is computed by backward induction from the terminal payoffs.

**u** = e^(σ · √Δt)

**p** = ( e^(r · Δt) − d ) / ( u − d )

Where `p` is the risk-neutral probability of an up move and `Δt = T/n`.

For American options, at each node the model takes the maximum of the hold value and the intrinsic value (early exercise). More steps → greater accuracy; 100–200 steps is typically sufficient.

### When to use which

| Scenario | Recommended model |
|----------|------------------|
| European call or put, fast pricing | Black-Scholes |
| American option | Binomial Tree |
| Validating Black-Scholes output | Binomial Tree (results converge as steps → ∞) |

## Variable Reference

| Symbol | Parameter | Description |
|--------|-----------|-------------|
| S | `underlying_asset_price` | Current price of the underlying asset |
| K | `strike_price` | Strike price of the option |
| T | `time_to_expiration` | Time to expiration in years |
| r | `risk_free_rate` | Annual risk-free interest rate |
| σ | `volatility` | Annual volatility of the underlying asset |
| N(·) | — | Cumulative standard normal distribution |

## Dependencies

- `numpy` — numerical computations
- `scipy` — normal distribution CDF (Black-Scholes)
- `pandas` — data handling
- `matplotlib` — plotting
- `pytest` — testing
- `black` — code formatting
- `ruff` — linting
