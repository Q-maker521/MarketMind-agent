from statistics import mean, stdev


def calculate_basic_indicators(market_data: dict) -> dict:
    candles = market_data["candles"]
    closes = [float(candle["close"]) for candle in candles]
    if len(closes) < 2:
        raise ValueError("At least two close prices are required.")

    start_price = closes[0]
    end_price = closes[-1]
    period_return = (end_price / start_price) - 1
    daily_returns = [(closes[index] / closes[index - 1]) - 1 for index in range(1, len(closes))]
    annualized_volatility = stdev(daily_returns) * (252**0.5) if len(daily_returns) > 1 else 0.0
    ma20 = mean(closes[-20:]) if len(closes) >= 20 else mean(closes)
    ma60 = mean(closes[-60:]) if len(closes) >= 60 else mean(closes)
    max_drawdown = _max_drawdown(closes)

    if end_price >= ma20 >= ma60:
        trend_label = "price_above_ma20_and_ma60"
    elif end_price >= ma20:
        trend_label = "price_above_ma20"
    else:
        trend_label = "price_below_ma20"

    return {
        "symbol": market_data["symbol"],
        "candles": len(candles),
        "start_price": round(start_price, 2),
        "end_price": round(end_price, 2),
        "ma20": round(ma20, 2),
        "ma60": round(ma60, 2),
        "period_return": round(period_return, 4),
        "annualized_volatility": round(annualized_volatility, 4),
        "max_drawdown": round(max_drawdown, 4),
        "trend_label": trend_label,
    }


def format_indicator_summary(indicators: dict) -> str:
    return (
        f"MA20={indicators['ma20']}, MA60={indicators['ma60']}, "
        f"区间收益={indicators['period_return']:.2%}, "
        f"年化波动率={indicators['annualized_volatility']:.2%}, "
        f"最大回撤={indicators['max_drawdown']:.2%}"
    )


def _max_drawdown(closes: list[float]) -> float:
    peak = closes[0]
    max_drawdown = 0.0
    for close in closes:
        peak = max(peak, close)
        drawdown = (close / peak) - 1
        max_drawdown = min(max_drawdown, drawdown)
    return max_drawdown
