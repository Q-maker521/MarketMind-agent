import json
from typing import Any, Protocol
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from app.core.config import settings


class LLMProvider(Protocol):
    name: str

    def generate_report_commentary(
        self,
        task: dict[str, Any],
        indicators: dict[str, Any],
        backtest: dict[str, Any],
        news_summary: dict[str, Any],
    ) -> dict[str, Any]:
        """Return normalized report commentary."""


class LLMProviderError(Exception):
    """Raised when an LLM provider cannot return normalized commentary."""


class MockLLMProvider:
    name = "mock"

    def generate_report_commentary(
        self,
        task: dict[str, Any],
        indicators: dict[str, Any],
        backtest: dict[str, Any],
        news_summary: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "summary": (
                f"区间收益 {indicators['period_return']:.2%}，"
                f"年化波动率 {indicators['annualized_volatility']:.2%}，"
                f"买入并持有收益 {backtest['total_return']:.2%}。"
            ),
            "stance": "neutral",
            "confidence": 0.74,
            "source": "mock_llm",
            "model": "deterministic-template",
        }


class OpenAICompatibleLLMProvider:
    name = "openai_compatible"

    def __init__(self, api_base_url: str, api_key: str, model: str, timeout_seconds: int) -> None:
        self._api_base_url = api_base_url.rstrip("/") + "/"
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate_report_commentary(
        self,
        task: dict[str, Any],
        indicators: dict[str, Any],
        backtest: dict[str, Any],
        news_summary: dict[str, Any],
    ) -> dict[str, Any]:
        if not self._api_key:
            raise LLMProviderError("LLM API key is not configured.")
        if not self._model:
            raise LLMProviderError("LLM model is not configured.")

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an investment research assistant. Return compact JSON only. "
                        "Do not provide investment advice. Use stance values: bullish, neutral, bearish."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": task,
                            "indicators": indicators,
                            "backtest": backtest,
                            "news_summary": news_summary,
                            "required_schema": {
                                "summary": "short Chinese summary",
                                "stance": "bullish|neutral|bearish",
                                "confidence": "number between 0 and 1",
                            },
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                },
            ],
            "temperature": 0.2,
            "max_tokens": 512,
        }
        request = Request(
            urljoin(self._api_base_url, "chat/completions"),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (TimeoutError, OSError, URLError, json.JSONDecodeError) as exc:
            raise LLMProviderError(f"LLM request failed: {exc}") from exc

        try:
            content = response_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(f"LLM response missing message content: {exc}") from exc

        return _normalize_llm_content(content, self._model)


def get_llm_provider() -> LLMProvider:
    provider_name = settings.llm_provider.lower()
    if (
        provider_name == "openai_compatible"
        and settings.llm_api_base_url
        and settings.llm_api_key
        and settings.llm_model
    ):
        return OpenAICompatibleLLMProvider(
            settings.llm_api_base_url,
            settings.llm_api_key,
            settings.llm_model,
            settings.llm_timeout_seconds,
        )
    return MockLLMProvider()


def _normalize_llm_content(content: str, model: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {"summary": content}

    summary = str(parsed.get("summary", "")).strip()
    if not summary:
        raise LLMProviderError("LLM response summary is empty.")

    stance = str(parsed.get("stance", "neutral")).strip().lower()
    if stance not in {"bullish", "neutral", "bearish"}:
        stance = "neutral"

    try:
        confidence = float(parsed.get("confidence", 0.65))
    except (TypeError, ValueError):
        confidence = 0.65
    confidence = max(0.0, min(confidence, 1.0))

    return {
        "summary": summary,
        "stance": stance,
        "confidence": confidence,
        "source": "openai_compatible",
        "model": model,
    }
