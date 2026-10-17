"""Run a scripted 10-turn conversation and log how input tokens grow per turn."""

import csv
from pathlib import Path

from shopai.config import get_settings
from shopai.llm import call
from shopai.log import configure_logging

MODEL = "claude-sonnet-5-5"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"

# Each turn references something from an earlier turn, so the model actually needs the
# resent history to answer correctly - not just filler text.
TURNS = [
    "My name is Priya and I bought a Homiva kettle last week.",
    "It arrived with a cracked lid. What's your return policy on that?",
    "Okay. How many days do I have to request a return?",
    "What's my name again?",
    "I also have a Kitchora air fryer. Does the same return window apply to it?",
    "Which of my two products arrived damaged?",
    "If I return the kettle, will I get a refund or does it have to be a replacement?",
    "Summarize what we've discussed so far in two sentences.",
    "One more thing - what was the first product I mentioned?",
    "Thanks, that's everything I needed.",
]


def main() -> None:
    configure_logging(get_settings().log_level)

    history: list[dict] = []
    rows = []

    for turn_number, user_message in enumerate(TURNS, start=1):
        history.append({"role": "user", "content": user_message})

        result = call(history, model=MODEL, max_tokens=300)
        history.append({"role": "assistant", "content": result.text})

        rows.append(
            {
                "turn": turn_number,
                "user_message": user_message,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
            }
        )
        print(f"Turn {turn_number}: input_tokens={result.input_tokens}")
        print(f"  You: {user_message}")
        print(f"  Claude: {result.text}\n")

    out_path = RESULTS_DIR / "token_growth.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["turn", "user_message", "input_tokens", "output_tokens"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved to {out_path}\n")
    print("Input tokens per turn:")
    max_tokens = max(r["input_tokens"] for r in rows)
    for r in rows:
        bar_len = round(r["input_tokens"] / max_tokens * 50)
        print(f"  turn {r['turn']:2d} | {'#' * bar_len} {r['input_tokens']}")


if __name__ == "__main__":
    main()
