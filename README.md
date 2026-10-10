# Brent futures moving average backtest

A small Python script that backtests a 20/50 day moving average crossover on Brent crude futures.

I'm a petroleum engineering student and wanted to see how a basic trend-following rule behaves on an asset I actually study. The idea is simple: hold Brent when the 20-day average is above the 50-day average, stay out otherwise. Then compare that against just buying and holding.

## How it works

1. Downloads daily Brent futures prices (`BZ=F`) from Yahoo Finance using `yfinance`
2. Calculates the 20 and 50 day moving averages
3. Goes long when the fast average is above the slow one, flat otherwise
4. Shifts the signal by one day so each trade uses only yesterday's information
5. Compares the strategy with buy and hold: total return, annual return, max drawdown, number of trades and win rate

I used Brent instead of WTI (`CL=F`) because WTI futures went negative in April 2020, which breaks percentage return calculations.

## Running it

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python backtest.py
```

It prints the results, saves them to `results.txt` and saves a chart as `chart.png`.

## Results

Period: 2010-03-16 to 2026-10-09

| | Strategy | Buy & hold |
|---|---|---|
| Total return | 206.3% | 34.4% |
| Annual return | 7.1% | 1.8% |
| Max drawdown | -49.1% | -84.7% |

Trades: 42, win rate: 38.1%

The strategy ended ahead mostly because it sat out the 2014-16 and 2020 crashes, where buy and hold lost most of its value. Its own max drawdown of -49% came after the 2022 peak, when prices moved sideways and the crossover kept switching in and out. Only about 38% of trades made money, so the gains came from a few long trends rather than frequent wins.

![chart](chart.png)

## Limitations

- No transaction costs or slippage. Real trading would reduce the returns.
- Yahoo's `BZ=F` is a continuous front-month series stitched together, so there are small jumps when the contract rolls over.
- Parameters (20/50) were picked because they are common, not optimised. Tuning them on the same data would overfit.
- Long-only and one rule. This is a learning project, not a trading system.

## Files

- `backtest.py` - the whole backtest
- `requirements.txt` - packages needed