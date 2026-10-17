"""A command-line chat that resends the full message history every turn."""

import anthropic

from shopai.config import get_settings

MODEL = "claude-sonnet-5-5"


def main() -> None:
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())

    history: list[dict] = []
    print("Chatting with Claude. Type 'quit' to exit.\n")

    turn = 0
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break

        turn += 1
        history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=history,
        )
        reply = next(block.text for block in response.content if block.type == "text")
        history.append({"role": "assistant", "content": reply})

        print(f"Claude: {reply}\n")
        print(
            f"[turn {turn}] input_tokens={response.usage.input_tokens} "
            f"output_tokens={response.usage.output_tokens}\n"
        )


if __name__ == "__main__":
    main()
