"""Report token count, cost estimate, and tokens-per-word ratio for a text file."""

import argparse
from pathlib import Path

import anthropic

from shopai.config import get_settings

MODEL = "claude-sonnet-5-5"
INPUT_PRICE_PER_TOKEN = 2.00 / 1_000_000  # Sonnet 5.5 input price: $2.00 / 1M tokens


def count_tokens(client: anthropic.Anthropic, text: str) -> int:
    response = client.messages.count_tokens(
        model=MODEL,
        messages=[{"role": "user", "content": text}],
    )
    return response.input_tokens


def find_outlier_word(client: anthropic.Anthropic, words: list[str]) -> tuple[str, int]:
    """Find the unique word with the highest token count. One API call per unique word."""
    best_word, best_tokens = "", 0
    for word in dict.fromkeys(words):  # de-dupe, preserve order
        tokens = count_tokens(client, word)
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

    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())

    tokens = count_tokens(client, text)
    cost = tokens * INPUT_PRICE_PER_TOKEN
    ratio = tokens / len(words) if words else 0.0

    print(f"File:            {args.path}")
    print(f"Words:           {len(words):,}")
    print(f"Tokens:          {tokens:,}")
    print(f"Tokens/word:     {ratio:.2f}")
    print(
        f"Est. input cost: ${cost:.6f} "
        f"(Sonnet 5.5 input pricing, ${INPUT_PRICE_PER_TOKEN * 1_000_000:.2f}/1M tokens)"
    )

    if args.find_outlier:
        word, word_tokens = find_outlier_word(client, words)
        print(f"Highest-token word: {word!r} -> {word_tokens} tokens")


if __name__ == "__main__":
    main()
