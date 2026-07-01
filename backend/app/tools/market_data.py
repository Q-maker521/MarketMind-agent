from datetime import UTC, date, datetime, timedelta
from math import sin
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import json

from app.core.config import settings


class MarketDataProvider(Protocol):
    name: str

    def get_daily_prices(self, symbol: str, time_range: str) -> dict:
        """Return normalized daily OHLCV data."""


class MarketDataProviderError(Exception):
    """Raised when a market data provider cannot return normalized data."""


class MockMarketDataProvider:
    name = "mock"

    def get_daily_prices(self, symbol: str, time_range: str) -> dict:
        return get_mock_daily_prices(symbol, time_range)


class AlphaVantageMarketDataProvider:
    name = "alpha_vantage"
    base_url = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def get_daily_prices(self, symbol: str, time_range: str) -> dict:
        if not self._api_key:
            raise MarketDataProviderError("Alpha Vantage API key is not configured.")

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper(),
            "outputsize": _alpha_vantage_output_size(time_range),
            "apikey": self._api_key,
        }
        url = f"{self.base_url}?{urlencode(params)}"

        try:
            with urlopen(url, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (TimeoutError, URLError, json.JSONDecodeError) as exc:
            raise MarketDataProviderError(f"Alpha Vantage request failed: {exc}") from exc

        series = payload.get("Time Series (Daily)")
        if not isinstance(series, dict):
            message = payload.get("Error Message") or payload.get("Note") or "Alpha Vantage returned no daily series."
            raise MarketDataProviderError(message)

        candles = []
        try:
            for trading_date, values in sorted(series.items()):
                candles.append(
                    {
                        "date": trading_date,
                        "open": round(float(values["1. open"]), 2),
                        "high": round(float(values["2. high"]), 2),
                        "low": round(float(values["3. low"]), 2),
                        "close": round(float(values["4. close"]), 2),
                        "volume": int(values["5. volume"]),
                    }
                )
        except (KeyError, TypeError, ValueError) as exc:
            raise MarketDataProviderError(f"Alpha Vantage returned malformed daily series: {exc}") from exc

        limit = _trading_days_for_range(time_range)
        candles = candles[-limit:]
        if len(candles) < 2:
            raise MarketDataProviderError("Alpha Vantage returned too few candles.")

        return {
            "symbol": symbol.upper(),
            "market": "US",
            "time_range": time_range,
            "candles": candles,
            "source": "alpha_vantage",
            "coverage": "complete" if len(candles) >= limit else "partial",
        }


class YahooFinanceMarketDataProvider:
    name = "yahoo_finance"
    base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"

    def get_daily_prices(self, symbol: str, time_range: str) -> dict:
        yahoo_symbol = symbol.strip().upper()
        params = {
            "range": _yahoo_range(time_range),
            "interval": "1d",
        }
        request = Request(
            f"{self.base_url}{yahoo_symbol}?{urlencode(params)}",
            headers={"User-Agent": "Mozilla/5.0"},
        )

        try:
            with urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (TimeoutError, HTTPError, URLError, json.JSONDecodeError) as exc:
            raise MarketDataProviderError(f"Yahoo Finance request failed: {exc}") from exc

        chart = payload.get("chart", {})
        if chart.get("error"):
            raise MarketDataProviderError(f"Yahoo Finance returned error: {chart['error']}")

        try:
            result = chart["result"][0]
            timestamps = result["timestamp"]
            quote = result["indicators"]["quote"][0]
        except (KeyError, IndexError, TypeError) as exc:
            raise MarketDataProviderError(f"Yahoo Finance returned malformed chart data: {exc}") from exc

        candles = []
        try:
            for index, timestamp in enumerate(timestamps):
                close = quote["close"][index]
                if close is None:
                    continue
                candles.append(
                    {
                        "date": datetime.fromtimestamp(timestamp, UTC).date().isoformat(),
                        "open": round(float(quote["open"][index]), 2),
                        "high": round(float(quote["high"][index]), 2),
                        "low": round(float(quote["low"][index]), 2),
                        "close": round(float(close), 2),
                        "volume": int(quote["volume"][index] or 0),
                    }
                )
        except (IndexError, KeyError, TypeError, ValueError) as exc:
            raise MarketDataProviderError(f"Yahoo Finance returned malformed daily series: {exc}") from exc

        limit = _trading_days_for_range(time_range)
        candles = candles[-limit:]
        if len(candles) < 2:
            raise MarketDataProviderError("Yahoo Finance returned too few candles.")

        return {
            "symbol": symbol.upper(),
            "market": "US",
            "time_range": time_range,
            "candles": candles,
            "source": "yahoo_finance",
            "coverage": "complete" if len(candles) >= limit else "partial",
        }


def get_market_data_provider() -> MarketDataProvider:
    provider_name = settings.market_data_provider.lower()
    if provider_name == "yahoo_finance":
        return YahooFinanceMarketDataProvider()
    if provider_name == "alpha_vantage" and settings.alpha_vantage_api_key:
        return AlphaVantageMarketDataProvider(settings.alpha_vantage_api_key)
    return MockMarketDataProvider()


def get_mock_daily_prices(symbol: str, time_range: str) -> dict:
    trading_days = _trading_days_for_range(time_range)
    base_price = _base_price_for_symbol(symbol)
    candles = []
    current_date = date(2026, 6, 30) - timedelta(days=trading_days + 40)
    index = 0

    while len(candles) < trading_days:
        current_date += timedelta(days=1)
        if current_date.weekday() >= 5:
            continue

        trend = index * 0.19
        seasonal = sin(index / 7) * 2.4
        close = round(base_price + trend + seasonal, 2)
        open_price = round(close - 0.65 + sin(index / 5) * 0.5, 2)
        high = round(max(open_price, close) + 1.35, 2)
        low = round(min(open_price, close) - 1.2, 2)
        volume = int(52_000_000 + (sin(index / 9) + 1) * 8_000_000)

        candles.append(
            {
                "date": current_date.isoformat(),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )
        index += 1

    return {
        "symbol": symbol.upper(),
        "market": "US",
        "time_range": time_range,
        "candles": candles,
        "source": "mock_ohlcv",
        "coverage": "complete",
    }


def _alpha_vantage_output_size(time_range: str) -> str:
    if time_range == "1y":
        return "full"
    return "compact"


def _trading_days_for_range(time_range: str) -> int:
    ranges = {
        "1mo": 21,
        "3mo": 63,
        "6mo": 126,
        "1y": 252,
    }
    return ranges.get(time_range, 126)


def _yahoo_range(time_range: str) -> str:
    ranges = {
        "1mo": "1mo",
        "3mo": "3mo",
        "6mo": "6mo",
        "1y": "1y",
    }
    return ranges.get(time_range, "6mo")


def _base_price_for_symbol(symbol: str) -> float:
    bases = {
        "AAPL": 185.0,
        "MSFT": 420.0,
        "NVDA": 118.0,
    }
    return bases.get(symbol.upper(), 100.0)

