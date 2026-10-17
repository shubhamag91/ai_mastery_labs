"""A command-line chat that resends the full message history every turn."""

from shopai.config import get_settings
from shopai.llm import call
from shopai.log import configure_logging

MODEL = "claude-sonnet-5-5"


def main() -> None:
    configure_logging(get_settings().log_level)

    history: list[dict] = []
    print("Chatting with Claude. Type 'quit' to exit.\n")

    turn = 0
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break

        turn += 1
        history.append({"role": "user", "content": user_input})

        result = call(history, model=MODEL, max_tokens=1024)
        history.append({"role": "assistant", "content": result.text})

        print(f"Claude: {result.text}\n")
        print(
            f"[turn {turn}] input_tokens={result.input_tokens} "
            f"output_tokens={result.output_tokens}\n"
        )


if __name__ == "__main__":
    main()
