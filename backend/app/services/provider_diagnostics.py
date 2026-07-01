from datetime import UTC, datetime
from time import perf_counter

from app.core.config import settings
from app.models.schemas import (
    ProviderDiagnosticCheck,
    ProviderDiagnosticsRequest,
    ProviderDiagnosticsResponse,
)
from app.tools.llm import LLMProviderError, get_llm_provider
from app.tools.market_data import MarketDataProviderError, get_market_data_provider


def run_provider_diagnostics(payload: ProviderDiagnosticsRequest) -> ProviderDiagnosticsResponse:
    return ProviderDiagnosticsResponse(
        created_at=datetime.now(UTC),
        market_data=_check_market_data(payload),
        llm=_check_llm(payload),
    )


def _check_market_data(payload: ProviderDiagnosticsRequest) -> ProviderDiagnosticCheck:
    provider = get_market_data_provider()
    provider_name = provider.__class__.__name__
    configured = settings.market_data_provider.lower() == "alpha_vantage" and bool(settings.alpha_vantage_api_key)
    started_at = perf_counter()

    try:
        market_data = provider.get_daily_prices(payload.symbol, payload.time_range)
    except MarketDataProviderError as exc:
        return ProviderDiagnosticCheck(
            name="market_data",
            provider=provider_name,
            configured=configured,
            status="failed",
            latency_ms=_elapsed_ms(started_at),
            summary="行情数据源诊断失败。",
            error_message=str(exc),
        )

    candles = market_data.get("candles", [])
    return ProviderDiagnosticCheck(
        name="market_data",
        provider=provider_name,
        configured=configured,
        status="success",
        latency_ms=_elapsed_ms(started_at),
        summary=f"成功获取 {len(candles)} 条 {payload.symbol.upper()} 日线数据。",
        metadata={
            "symbol": market_data.get("symbol"),
            "source": market_data.get("source"),
            "coverage": market_data.get("coverage"),
            "candles": len(candles),
        },
    )


def _check_llm(payload: ProviderDiagnosticsRequest) -> ProviderDiagnosticCheck:
    provider = get_llm_provider()
    provider_name = provider.__class__.__name__
    configured = (
        settings.llm_provider.lower() == "openai_compatible"
        and bool(settings.llm_api_base_url)
        and bool(settings.llm_api_key)
        and bool(settings.llm_model)
    )

    if not payload.include_llm:
        return ProviderDiagnosticCheck(
            name="llm",
            provider=provider_name,
            configured=configured,
            status="skipped",
            latency_ms=0,
            summary="已跳过模型诊断。",
        )

    started_at = perf_counter()
    task = {
        "symbol": payload.symbol.upper(),
        "market": "US",
        "time_range": payload.time_range,
        "question": "Provider diagnostic smoke test.",
    }
    indicators = {
        "period_return": 0.042,
        "annualized_volatility": 0.21,
        "latest_close": 100.0,
        "moving_average_20": 98.5,
        "moving_average_60": 95.2,
    }
    backtest = {
        "total_return": 0.039,
        "max_drawdown": -0.061,
        "start_price": 96.2,
        "end_price": 100.0,
    }
    news_summary = {
        "headline_count": 3,
        "sentiment": "neutral",
        "risk_keywords": ["earnings", "rates"],
    }

    try:
        commentary = provider.generate_report_commentary(task, indicators, backtest, news_summary)
    except LLMProviderError as exc:
        return ProviderDiagnosticCheck(
            name="llm",
            provider=provider_name,
            configured=configured,
            status="failed",
            latency_ms=_elapsed_ms(started_at),
            summary="模型生成诊断失败。",
            error_message=str(exc),
        )

    return ProviderDiagnosticCheck(
        name="llm",
        provider=provider_name,
        configured=configured,
        status="success",
        latency_ms=_elapsed_ms(started_at),
        summary="模型生成诊断成功。",
        metadata={
            "source": commentary.get("source"),
            "model": commentary.get("model"),
            "stance": commentary.get("stance"),
            "confidence": commentary.get("confidence"),
        },
    )


def _elapsed_ms(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)
