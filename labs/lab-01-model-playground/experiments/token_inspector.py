"""Report token count, cost estimate, and tokens-per-word ratio for a text file."""

import argparse
from pathlib import Path

from shopai.llm import PRICING
from shopai.llm import count_tokens as llm_count_tokens

MODEL = "claude-sonnet-5-5"


def find_outlier_word(words: list[str]) -> tuple[str, int]:
    """Find the unique word with the highest token count. One API call per unique word."""
    best_word, best_tokens = "", 0
    for word in dict.fromkeys(words):  # de-dupe, preserve order
        tokens = llm_count_tokens([{"role": "user", "content": word}], model=MODEL)
        if tokens > best_tokens:
            best_word, best_tokens = word, tokens
    return best_word, best_tokens


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect token count and cost for a text file.")
    parser.add_argument("path", type=Path, help="Path to a UTF-8 text file.")
    parser.add_argument(
        "--find-outlier",
        action="store_true",
        help="Also find the highest-token unique word (one extra API call per unique word).",
    )
    args = parser.parse_args()

    text = args.path.read_text(encoding="utf-8")
    words = text.split()

    tokens = llm_count_tokens([{"role": "user", "content": text}], model=MODEL)
    input_price_per_token, _ = PRICING[MODEL]
    cost = tokens * input_price_per_token
    ratio = tokens / len(words) if words else 0.0

    print(f"File:            {args.path}")
    print(f"Words:           {len(words):,}")
    print(f"Tokens:          {tokens:,}")
    print(f"Tokens/word:     {ratio:.2f}")
    print(
        f"Est. input cost: ${cost:.6f} "
        f"(Sonnet 5.5 input pricing, ${input_price_per_token * 1_000_000:.2f}/1M tokens)"
    )

    if args.find_outlier:
        word, word_tokens = find_outlier_word(words)
        print(f"Highest-token word: {word!r} -> {word_tokens} tokens")


if __name__ == "__main__":
    main()
