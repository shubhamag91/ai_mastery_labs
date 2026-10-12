"""A small DeepSeek client for the data generator: JSON replies, retries, token accounting.

DeepSeek's API accepts OpenAI's request format, so the `openai` library talks to it when
pointed at DeepSeek's base URL.
"""

import json
import time

from openai import OpenAI

from shopai.config import get_settings
from shopai.log import get_logger

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-v4-pro"
# US$ per million tokens at peak rates (off-peak is half). Source:
# https://api-docs.deepseek.com/quick_start/pricing, read on 2026-10-11.
PRICE_INPUT_PER_M = 1.32
PRICE_OUTPUT_PER_M = 3.96

log = get_logger(__name__)
usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0}


def cost_usd() -> float:
    """Cost of every call so far, at peak rates: an upper bound."""
    return (
        usage["input_tokens"] * PRICE_INPUT_PER_M + usage["output_tokens"] * PRICE_OUTPUT_PER_M
    ) / 1_000_000


def chat_json(
    system: str, user: str, max_tokens: int = 8000, attempts: int = 3, thinking: bool = False
) -> dict:
    """Send one request and return the reply parsed as JSON. Retries on errors and bad JSON.

    Thinking is off by default: deepseek-v4-pro reasons before answering unless told not to,
    and in the pilot that reasoning was about 7 of every 8 output tokens billed. Writing
    reviews doesn't need it.
    """
    key = get_settings().deepseek_api_key
    if key is None:
        raise SystemExit("DEEPSEEK_API_KEY is not set in .env")
    client = OpenAI(api_key=key.get_secret_value(), base_url=BASE_URL, timeout=600)

    for attempt in range(1, attempts + 1):
        started = time.monotonic()
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                temperature=1.0,
                extra_body={"thinking": {"type": "enabled" if thinking else "disabled"}},
            )
        except Exception as error:  # network trouble or an API error: wait, then retry
            log.warning("llm_error", attempt=attempt, error=str(error)[:200])
            time.sleep(5 * attempt)
            continue

        usage["calls"] += 1
        usage["input_tokens"] += response.usage.prompt_tokens
        usage["output_tokens"] += response.usage.completion_tokens
        choice = response.choices[0]
        log.info(
            "llm_call",
            model=MODEL,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            seconds=round(time.monotonic() - started, 1),
            finish_reason=choice.finish_reason,
        )
        try:
            return json.loads(choice.message.content)
        except (json.JSONDecodeError, TypeError):
            log.warning("llm_bad_json", attempt=attempt, finish_reason=choice.finish_reason)

    raise RuntimeError(f"No valid JSON reply after {attempts} attempts")
