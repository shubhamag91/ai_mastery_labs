"""Compare models, prompt placement, and extended thinking on one summarization task."""

from dataclasses import dataclass
from pathlib import Path

from shopai.config import get_settings
from shopai.llm import call
from shopai.log import configure_logging

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


def run_config(
    config_name: str,
    model: str,
    ticket_text: str,
    *,
    instruction_in_system: bool,
    thinking: bool,
) -> RunResult:
    if instruction_in_system:
        system = INSTRUCTION
        user_content = ticket_text
    else:
        system = None
        user_content = f"{INSTRUCTION}\n\nTicket:\n{ticket_text}"

    kwargs = {}
    if thinking:
        kwargs["thinking"] = {"type": "adaptive"}
        kwargs["output_config"] = {"effort": "high"}

    llm_result = call(
        [{"role": "user", "content": user_content}],
        model=model,
        system=system,
        max_tokens=16000 if thinking else 1024,
        **kwargs,
    )

    result = RunResult(
        config_name=config_name,
        model=model,
        summary=llm_result.text,
        latency_seconds=llm_result.latency_seconds,
        input_tokens=llm_result.input_tokens,
        output_tokens=llm_result.output_tokens,
        thinking_tokens=llm_result.thinking_tokens,
        cost_usd=llm_result.cost_usd,
    )

    slug = config_name.lower().replace(" ", "_").replace("/", "_")
    out_path = RESULTS_DIR / f"summary_{slug}.txt"
    out_path.write_text(result.summary, encoding="utf-8")

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

    configure_logging(get_settings().log_level)

    with open("data/reviews.csv", newline="", encoding="utf-8") as f:
        rows = {row["review_id"]: row for row in csv.DictReader(f)}
    ticket_text = rows["59"]["text"]

    configs = [
        ("fast model (Haiku 5.5)", "claude-haiku-5-5", True, False),
        ("capable model (Opus 5.5)", "claude-opus-5-5", True, False),
        ("capable, instruction in messages", "claude-opus-5-5", False, False),
        ("capable, extended thinking", "claude-opus-5-5", True, True),
    ]

    results = [
        run_config(name, model, ticket_text, instruction_in_system=in_system, thinking=thinking)
        for name, model, in_system, thinking in configs
    ]

    print_table(results)


if __name__ == "__main__":
    main()
