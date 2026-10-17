"""Test doubles for the Anthropic SDK shapes shopai.llm depends on. No network, ever."""

from dataclasses import dataclass


@dataclass
class FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class FakeOutputTokensDetails:
    thinking_tokens: int = 0


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int
    output_tokens_details: FakeOutputTokensDetails | None = None


@dataclass
class FakeResponse:
    content: list[FakeTextBlock]
    usage: FakeUsage


@dataclass
class FakeCountTokensResponse:
    input_tokens: int


class FakeMessagesClient:
    """Stands in for `anthropic.Anthropic(...).messages`. Returns a fixed response
    and records every call it received, so a test can assert on what was sent."""

    def __init__(self, response: FakeResponse, token_count: int = 0) -> None:
        self.response = response
        self.token_count = token_count
        self.calls: list[dict] = []
        self.count_tokens_calls: list[dict] = []

    def create(self, **kwargs: object) -> FakeResponse:
        self.calls.append(kwargs)
        return self.response

    def count_tokens(self, **kwargs: object) -> FakeCountTokensResponse:
        self.count_tokens_calls.append(kwargs)
        return FakeCountTokensResponse(input_tokens=self.token_count)


def fake_response(
    text: str = "a fake reply",
    input_tokens: int = 10,
    output_tokens: int = 5,
    thinking_tokens: int = 0,
) -> FakeResponse:
    return FakeResponse(
        content=[FakeTextBlock(text=text)],
        usage=FakeUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            output_tokens_details=FakeOutputTokensDetails(thinking_tokens=thinking_tokens),
        ),
    )
