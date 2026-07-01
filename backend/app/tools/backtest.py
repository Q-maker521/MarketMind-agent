def run_buy_and_hold_backtest(market_data: dict) -> dict:
    candles = market_data["candles"]
    if len(candles) < 2:
        raise ValueError("At least two candles are required.")

    start = candles[0]
    end = candles[-1]
    start_price = float(start["close"])
    end_price = float(end["close"])
    total_return = (end_price / start_price) - 1
    max_drawdown = _max_drawdown([float(candle["close"]) for candle in candles])

    return {
        "strategy": "buy_and_hold",
        "symbol": market_data["symbol"],
        "start_date": start["date"],
        "end_date": end["date"],
        "start_price": round(start_price, 2),
        "end_price": round(end_price, 2),
        "holding_days": len(candles),
        "total_return": round(total_return, 4),
        "max_drawdown": round(max_drawdown, 4),
    }


def format_backtest_summary(result: dict) -> str:
    return (
        f"买入并持有收益={result['total_return']:.2%}, "
        f"最大回撤={result['max_drawdown']:.2%}, "
        f"区间={result['start_date']} 至 {result['end_date']}"
    )


def _max_drawdown(closes: list[float]) -> float:
    peak = closes[0]
    max_drawdown = 0.0
    for close in closes:
        peak = max(peak, close)
        drawdown = (close / peak) - 1
        max_drawdown = min(max_drawdown, drawdown)
    return max_drawdown
