"""One place to call Claude from: logging, cost, and an injectable client live here."""

import time
from dataclasses import dataclass
from typing import Protocol

from shopai.config import get_settings
from shopai.log import get_logger

log = get_logger(__name__)

# (input $/token, output $/token). Add a model here once, not in every script that uses it.
PRICING = {
    "claude-sonnet-5-5": (2.00 / 1_000_000, 10.00 / 1_000_000),
    "claude-opus-5-5": (4.00 / 1_000_000, 20.00 / 1_000_000),
    "claude-haiku-5-5": (0.10 / 1_000_000, 0.50 / 1_000_000),
    "claude-haiku-4-5": (1.00 / 1_000_000, 5.00 / 1_000_000),
}


@dataclass
class LlmResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    cost_usd: float
    latency_seconds: float


class MessagesClient(Protocol):
    """The one piece of the Anthropic SDK this module depends on. A fake client only
    needs to implement this shape - see tests/fakes.py."""

    def create(self, **kwargs: object) -> object: ...
    def count_tokens(self, **kwargs: object) -> object: ...


def _cost(model: str, input_tokens: int, output_tokens: int) -> float:
    input_price, output_price = PRICING[model]
    return input_tokens * input_price + output_tokens * output_price


def _default_client() -> MessagesClient:
    import anthropic

    settings = get_settings()
    return anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value()).messages


def count_tokens(
    messages: list[dict],
    *,
    model: str = "claude-sonnet-5-5",
    system: str | None = None,
    client: MessagesClient | None = None,
) -> int:
    """Count tokens for a would-be request without running inference - free, no cost field."""
    if client is None:
        client = _default_client()

    kwargs: dict = {"model": model, "messages": messages}
    if system is not None:
        kwargs["system"] = system

    return client.count_tokens(**kwargs).input_tokens


def call(
    messages: list[dict],
    *,
    model: str = "claude-sonnet-5-5",
    system: str | None = None,
    max_tokens: int = 1024,
    thinking: dict | None = None,
    output_config: dict | None = None,
    extra_body: dict | None = None,
    client: MessagesClient | None = None,
) -> LlmResult:
    """Call the model and return a typed result. Logs one structured line per call.

    `client` is injectable: pass a fake with a `.create()` method in tests, and no
    real client is ever constructed, so tests need no API key and no network.
    """
    if client is None:
        client = _default_client()

    kwargs: dict = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system is not None:
        kwargs["system"] = system
    if thinking is not None:
        kwargs["thinking"] = thinking
    if output_config is not None:
        kwargs["output_config"] = output_config
    if extra_body is not None:
        kwargs["extra_body"] = extra_body

    start = time.perf_counter()
    response = client.create(**kwargs)
    latency = time.perf_counter() - start

    text = next(block.text for block in response.content if block.type == "text")
    usage = response.usage
    thinking_tokens = (
        (usage.output_tokens_details.thinking_tokens or 0) if usage.output_tokens_details else 0
    )
    cost = _cost(model, usage.input_tokens, usage.output_tokens)

    log.info(
        "llm_call",
        model=model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        thinking_tokens=thinking_tokens,
        cost_usd=cost,
        latency_s=round(latency, 3),
    )

    return LlmResult(
        text=text,
        model=model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        thinking_tokens=thinking_tokens,
        cost_usd=cost,
        latency_seconds=latency,
    )
