"""Compare models, prompt placement, and extended thinking on one summarization task."""

import time
from dataclasses import dataclass
from pathlib import Path

import anthropic

from shopai.config import get_settings

# (input $/1M tokens, output $/1M tokens)
PRICING = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-opus-5-5": (4.00, 20.00),
}

INSTRUCTION = (
    "Summarize this customer support ticket in 3-5 sentences. Capture the main "
    "complaint, exactly what the customer wants as resolution, and any key details "
    "a support agent would need to act on it."
)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


@dataclass
class RunResult:
    config_name: str
    model: str
    summary: str
    latency_seconds: float
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    cost_usd: float


def call(
    client: anthropic.Anthropic,
    model: str,
    ticket_text: str,
    *,
    instruction_in_system: bool,
    thinking: bool,
) -> tuple[str, float, object]:
    if instruction_in_system:
        system = INSTRUCTION
        user_content = ticket_text
    else:
        system = None
        user_content = f"{INSTRUCTION}\n\nTicket:\n{ticket_text}"

    kwargs = {}
    if system is not None:
        kwargs["system"] = system
    if thinking:
        kwargs["thinking"] = {"type": "adaptive"}
        kwargs["output_config"] = {"effort": "high"}

    start = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=16000 if thinking else 1024,
        messages=[{"role": "user", "content": user_content}],
        **kwargs,
    )
    latency = time.perf_counter() - start

    summary = next(block.text for block in response.content if block.type == "text")
    return summary, latency, response.usage


def run_config(
    client: anthropic.Anthropic,
    config_name: str,
    model: str,
    ticket_text: str,
    *,
    instruction_in_system: bool,
    thinking: bool,
) -> RunResult:
    summary, latency, usage = call(
        client,
        model,
        ticket_text,
        instruction_in_system=instruction_in_system,
        thinking=thinking,
    )
    thinking_tokens = (
        (usage.output_tokens_details.thinking_tokens or 0) if usage.output_tokens_details else 0
    )
    input_price, output_price = PRICING[model]
    cost = (usage.input_tokens * input_price + usage.output_tokens * output_price) / 1_000_000

    result = RunResult(
        config_name=config_name,
        model=model,
        summary=summary,
        latency_seconds=latency,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        thinking_tokens=thinking_tokens,
        cost_usd=cost,
    )

    slug = config_name.lower().replace(" ", "_").replace("/", "_")
    out_path = RESULTS_DIR / f"summary_{slug}.txt"
    out_path.write_text(summary, encoding="utf-8")

    return result


def print_table(results: list[RunResult]) -> None:
    header = (
        f"{'Configuration':<28} {'Model':<18} {'Latency(s)':>10} {'In tok':>7} "
        f"{'Out tok':>8} {'Think tok':>10} {'Cost($)':>9}"
    )
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r.config_name:<28} {r.model:<18} {r.latency_seconds:>10.2f} "
            f"{r.input_tokens:>7} {r.output_tokens:>8} {r.thinking_tokens:>10} {r.cost_usd:>9.5f}"
        )
    print()
    for r in results:
        print(f"=== {r.config_name} ({r.model}) ===")
        print(r.summary)
        print()


def main() -> None:
    import csv

    with open("data/reviews.csv", newline="", encoding="utf-8") as f:
        rows = {row["review_id"]: row for row in csv.DictReader(f)}
    ticket_text = rows["59"]["text"]

    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())

    configs = [
        ("fast model (Haiku 5.5)", "claude-haiku-5-5", True, False),
        ("capable model (Opus 5.5)", "claude-opus-5-5", True, False),
        ("capable, instruction in messages", "claude-opus-5-5", False, False),
        ("capable, extended thinking", "claude-opus-5-5", True, True),
    ]

    results = [
        run_config(
            client,
            name,
            model,
            ticket_text,
            instruction_in_system=in_system,
            thinking=thinking,
        )
        for name, model, in_system, thinking in configs
    ]

    print_table(results)


if __name__ == "__main__":
    main()
