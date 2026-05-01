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
