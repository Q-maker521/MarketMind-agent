from datetime import date, timedelta
from math import sin
import ssl
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi
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


class TwelveDataMarketDataProvider:
    name = "twelve_data"
    base_url = "https://api.twelvedata.com/time_series"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key or "demo"

    def get_daily_prices(self, symbol: str, time_range: str) -> dict:
        params = {
            "symbol": symbol.upper(),
            "interval": "1day",
            "outputsize": _trading_days_for_range(time_range),
            "apikey": self._api_key,
        }
        url = f"{self.base_url}?{urlencode(params)}"
        payload = _load_json(url, "Twelve Data")
        if payload.get("status") == "error":
            raise MarketDataProviderError(payload.get("message") or "Twelve Data returned an error.")

        values = payload.get("values")
        if not isinstance(values, list):
            raise MarketDataProviderError("Twelve Data returned no daily series.")

        candles = []
        try:
            for values_by_date in reversed(values):
                candles.append(
                    {
                        "date": values_by_date["datetime"],
                        "open": round(float(values_by_date["open"]), 2),
                        "high": round(float(values_by_date["high"]), 2),
                        "low": round(float(values_by_date["low"]), 2),
                        "close": round(float(values_by_date["close"]), 2),
                        "volume": int(float(values_by_date.get("volume") or 0)),
                    }
                )
        except (KeyError, TypeError, ValueError) as exc:
            raise MarketDataProviderError(f"Twelve Data returned malformed daily series: {exc}") from exc

        limit = _trading_days_for_range(time_range)
        candles = candles[-limit:]
        if len(candles) < 2:
            raise MarketDataProviderError("Twelve Data returned too few candles.")

        return {
            "symbol": symbol.upper(),
            "market": "US",
            "time_range": time_range,
            "candles": candles,
            "source": "twelve_data",
            "coverage": "complete" if len(candles) >= limit else "partial",
        }


def get_market_data_provider() -> MarketDataProvider:
    provider_name = settings.market_data_provider.lower()
    if provider_name == "twelve_data":
        return TwelveDataMarketDataProvider(settings.twelve_data_api_key)
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


def _base_price_for_symbol(symbol: str) -> float:
    bases = {
        "AAPL": 185.0,
        "MSFT": 420.0,
        "NVDA": 118.0,
    }
    return bases.get(symbol.upper(), 100.0)


def _load_json(url: str, provider_name: str) -> dict:
    context = ssl.create_default_context(cafile=certifi.where())
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    try:
        with urlopen(request, timeout=15, context=context) as response:
            return json.loads(response.read().decode("utf-8"))
    except (TimeoutError, HTTPError, URLError, json.JSONDecodeError) as exc:
        raise MarketDataProviderError(f"{provider_name} request failed: {exc}") from exc
