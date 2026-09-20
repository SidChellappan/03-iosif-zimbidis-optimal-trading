"""Proxy replication of the optimal-trading baseline and volatility correction."""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "spy.csv"
OUT = ROOT / "results.csv"


def load_prices() -> list[float]:
    prices = []
    with DATA.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            try:
                prices.append(float(row["AdjClose"]))
            except (KeyError, TypeError, ValueError):
                continue
    return prices


def rolling_mean(values: list[float], end: int, window: int) -> float:
    segment = values[max(0, end - window):end]
    return sum(segment) / len(segment) if segment else 0.0


def rolling_std(values: list[float], end: int, window: int) -> float:
    segment = values[max(0, end - window):end]
    return statistics.pstdev(segment) if len(segment) > 1 else 0.01


def simulate(returns: list[float], constant_vol: bool) -> list[float]:
    gamma = 4.0
    temporary_cost = 0.08
    impact_decay = 0.25
    liquidity = 0.08
    position = 0.0
    impact = 0.0
    pnl = []
    vols = [rolling_std(returns, i, 20) for i in range(len(returns))]
    fixed_vol = statistics.median(vols[30:]) or 0.01

    for i, realized_return in enumerate(returns):
        signal = rolling_mean(returns, i, 20)
        volatility = fixed_vol if constant_vol else max(vols[i], fixed_vol * 0.25)
        target = signal / (gamma * volatility * volatility + temporary_cost)
        trade_rate = (target - position) * 0.50
        step_pnl = position * realized_return
        step_pnl -= temporary_cost * trade_rate * trade_rate
        step_pnl -= liquidity * position * impact
        step_pnl -= liquidity * position * trade_rate
        position += trade_rate
        impact += liquidity * trade_rate - impact_decay * impact
        pnl.append(step_pnl)
    return pnl


def summarize(values: list[float]) -> dict[str, str | float]:
    mean = sum(values) / len(values)
    stdev = statistics.pstdev(values) or 1e-12
    return {
        "daily_mean_pnl": f"{mean:.8f}",
        "daily_pnl_std": f"{stdev:.8f}",
        "total_pnl": f"{sum(values):.8f}",
        "sharpe_like": f"{mean / stdev * math.sqrt(252):.6f}",
    }


def main() -> None:
    prices = load_prices()
    returns = [0.0] + [prices[i] / prices[i - 1] - 1.0 for i in range(1, len(prices))]
    baseline = summarize(simulate(returns, constant_vol=True))
    correction = summarize(simulate(returns, constant_vol=False))
    rows = [
        {"strategy": "constant_volatility_baseline", **baseline},
        {"strategy": "realized_volatility_correction", **correction},
    ]
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT.name}; price observations={len(prices)}")


if __name__ == "__main__":
    main()

