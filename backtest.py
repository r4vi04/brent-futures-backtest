# Moving average crossover backtest on Brent crude futures.
# Long when the fast average is above the slow one, flat otherwise.

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

TICKER = "BZ=F"        # Brent crude front-month futures on Yahoo Finance
START = "2010-01-01"
FAST = 20              # fast moving average window (days)
SLOW = 50              # slow moving average window (days)

# 1. Download daily prices
data = yf.download(TICKER, start=START, auto_adjust=True, progress=False)
price = data["Close"].squeeze().dropna()

df = pd.DataFrame({"price": price})

# 2. Moving averages
df["fast_ma"] = df["price"].rolling(FAST).mean()
df["slow_ma"] = df["price"].rolling(SLOW).mean()

# 3. Signal: 1 if fast is above slow, else 0
df["signal"] = (df["fast_ma"] > df["slow_ma"]).astype(int)

# 4. Position: act on yesterday's signal, so we never trade on
#    information we would not have had yet
df["position"] = df["signal"].shift(1)

# 5. Returns
df["market_ret"] = df["price"].pct_change()
df["strategy_ret"] = df["position"] * df["market_ret"]
df = df.dropna()

# 6. Equity curves (growth of 1 unit)
df["market_curve"] = (1 + df["market_ret"]).cumprod()
df["strategy_curve"] = (1 + df["strategy_ret"]).cumprod()


def summarise(returns):
    growth = (1 + returns).cumprod()
    total = growth.iloc[-1] - 1
    years = len(returns) / 252                      # about 252 trading days a year
    annual = growth.iloc[-1] ** (1 / years) - 1
    drawdown = growth / growth.cummax() - 1
    return total, annual, drawdown.min()


# 7. Trade level stats
df["entry"] = df["position"].diff() == 1            # position went 0 -> 1
df["trade_id"] = df["entry"].cumsum()
in_market = df[df["position"] == 1]
trade_returns = in_market.groupby("trade_id")["strategy_ret"].apply(
    lambda r: (1 + r).prod() - 1
)
num_trades = len(trade_returns)
win_rate = (trade_returns > 0).mean()

# 8. Print results
s_total, s_annual, s_dd = summarise(df["strategy_ret"])
m_total, m_annual, m_dd = summarise(df["market_ret"])

lines = [
    f"Ticker: {TICKER}   Period: {df.index[0].date()} to {df.index[-1].date()}",
    f"MA windows: {FAST} / {SLOW}",
    "",
    f"{'':<16}{'Strategy':>10}{'Buy & hold':>12}",
    f"{'Total return':<16}{s_total:>10.1%}{m_total:>12.1%}",
    f"{'Annual return':<16}{s_annual:>10.1%}{m_annual:>12.1%}",
    f"{'Max drawdown':<16}{s_dd:>10.1%}{m_dd:>12.1%}",
    "",
    f"Number of trades: {num_trades}",
    f"Win rate: {win_rate:.1%}",
]
report = "\n".join(lines)
print(report)
with open("results.txt", "w") as f:
    f.write(report)

# 9. Chart
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

ax1.plot(df.index, df["price"], label="Brent", color="black", linewidth=0.8)
ax1.plot(df.index, df["fast_ma"], label=f"{FAST}-day MA", linewidth=0.9)
ax1.plot(df.index, df["slow_ma"], label=f"{SLOW}-day MA", linewidth=0.9)
ax1.set_ylabel("Price (USD/bbl)")
ax1.legend()

ax2.plot(df.index, df["market_curve"], label="Buy & hold", color="gray")
ax2.plot(df.index, df["strategy_curve"], label="MA crossover")
ax2.set_ylabel("Growth of 1 unit")
ax2.legend()

plt.tight_layout()
plt.savefig("chart.png", dpi=150)
print("\nSaved chart.png and results.txt")
