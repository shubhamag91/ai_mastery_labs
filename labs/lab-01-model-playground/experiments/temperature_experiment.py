"""Measure how temperature affects agreement when classifying a review's theme."""

import argparse
from collections import Counter

import anthropic

from shopai.config import get_settings

# Sonnet 5.5 / Opus 5.5 run adaptive thinking by default and reject a non-default
# `temperature` (400) while thinking is active - thinking replaced manual sampling
# control on current-generation models. Haiku 4.5 has no thinking by default and
# still accepts temperature normally, so it's the model that can actually run this
# experiment's premise.
MODEL = "claude-haiku-4-5"

THEMES = [
    "delivery_delay",
    "damaged_on_arrival",
    "product_defect",
    "wrong_item",
    "returns_refunds",
    "customer_service",
    "value_for_money",
    "ease_of_use",
]

PROMPT_TEMPLATE = """Classify the main theme of this customer review. Pick exactly one \
theme from this list: {themes}

Review: "{review}"

Answer with only the theme id, nothing else."""

# With reasoning allowed, the model writes a short explanation before its answer.
# A longer generation gives per-token sampling noise more steps to compound, so it's
# more likely to surface real instability than a near single-token answer.
REASONING_PROMPT_TEMPLATE = """Classify the main theme of this customer review. Pick exactly \
one theme from this list: {themes}

Review: "{review}"

Think briefly about which theme fits best in one or two sentences, then end your answer \
with a final line in exactly this format: Final theme: <theme_id>"""


def classify_once(
    client: anthropic.Anthropic, review: str, temperature: float, reasoning: bool
) -> str:
    template = REASONING_PROMPT_TEMPLATE if reasoning else PROMPT_TEMPLATE
    response = client.messages.create(
        model=MODEL,
        max_tokens=200 if reasoning else 20,
        extra_body={"temperature": temperature},
        messages=[
            {
                "role": "user",
                "content": template.format(themes=", ".join(THEMES), review=review),
            }
        ],
    )
    text = next(block.text for block in response.content if block.type == "text").strip()
    if not reasoning:
        return text
    # Take the last theme id mentioned, since the model may name others while reasoning.
    found = [theme for theme in THEMES if theme in text]
    return found[-1] if found else text


def run_trials(
    client: anthropic.Anthropic, review: str, temperature: float, n: int, reasoning: bool
) -> Counter:
    answers = [classify_once(client, review, temperature, reasoning) for _ in range(n)]
    return Counter(answers)


def report(label: str, temperature: float, counts: Counter, n: int) -> None:
    most_common, most_common_count = counts.most_common(1)[0]
    agreement = most_common_count / n
    print(f"{label} @ temperature={temperature}")
    print(f"  distinct outputs: {len(counts)}")
    print(f"  most common:      {most_common!r} ({most_common_count}/{n})")
    print(f"  agreement rate:   {agreement:.0%}")
    print(f"  all counts:       {dict(counts)}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Temperature / non-determinism experiment.")
    parser.add_argument("--label", required=True, help="Short name for this review (for output).")
    parser.add_argument("--review", required=True, help="The review text to classify.")
    parser.add_argument("--n", type=int, default=20, help="Trials per temperature.")
    parser.add_argument(
        "--reasoning",
        action="store_true",
        help="Let the model reason briefly before answering (longer generation).",
    )
    args = parser.parse_args()

    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())

    for temperature in (0.0, 1.0):
        counts = run_trials(client, args.review, temperature, args.n, args.reasoning)
        report(args.label, temperature, counts, args.n)


if __name__ == "__main__":
    main()
