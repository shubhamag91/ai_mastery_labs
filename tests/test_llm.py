import json

import pytest
import structlog
from fakes import FakeMessagesClient, fake_response

from shopai.llm import call, count_tokens
from shopai.log import configure_logging


@pytest.fixture(autouse=True)
def reset_structlog():
    yield
    structlog.reset_defaults()


def read_lines(capsys):
    return [json.loads(line) for line in capsys.readouterr().out.splitlines()]


def test_no_api_key_needed_when_a_fake_client_is_given(monkeypatch):
    # The whole point of injection: this must work with no key and no network.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = FakeMessagesClient(fake_response(text="hello"))

    result = call([{"role": "user", "content": "hi"}], client=client)

    assert result.text == "hello"


def test_result_fields_come_from_the_response(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = FakeMessagesClient(
        fake_response(text="reply", input_tokens=100, output_tokens=50, thinking_tokens=20)
    )

    result = call([{"role": "user", "content": "hi"}], model="claude-sonnet-5-5", client=client)

    assert result.text == "reply"
    assert result.model == "claude-sonnet-5-5"
    assert result.input_tokens == 100
    assert result.output_tokens == 50
    assert result.thinking_tokens == 20
    assert result.latency_seconds >= 0


def test_cost_is_computed_from_the_pricing_table(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = FakeMessagesClient(fake_response(input_tokens=1_000_000, output_tokens=1_000_000))

    result = call([{"role": "user", "content": "hi"}], model="claude-opus-5-5", client=client)

    # Opus 5.5: $4.00 in + $20.00 out per 1M tokens (shopai.llm.PRICING)
    assert result.cost_usd == pytest.approx(24.00)


def test_missing_thinking_details_defaults_to_zero(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = fake_response()
    response.usage.output_tokens_details = None
    client = FakeMessagesClient(response)

    result = call([{"role": "user", "content": "hi"}], client=client)

    assert result.thinking_tokens == 0


def test_optional_kwargs_pass_through_to_the_client(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = FakeMessagesClient(fake_response())

    call(
        [{"role": "user", "content": "hi"}],
        model="claude-haiku-4-5",
        system="be terse",
        max_tokens=50,
        extra_body={"temperature": 0.0},
        client=client,
    )

    [sent] = client.calls
    assert sent["model"] == "claude-haiku-4-5"
    assert sent["system"] == "be terse"
    assert sent["max_tokens"] == 50
    assert sent["extra_body"] == {"temperature": 0.0}


def test_each_call_logs_one_structured_line(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    configure_logging("INFO")
    client = FakeMessagesClient(fake_response(input_tokens=10, output_tokens=5))

    call([{"role": "user", "content": "hi"}], model="claude-haiku-5-5", client=client)

    [line] = read_lines(capsys)
    assert line["event"] == "llm_call"
    assert line["model"] == "claude-haiku-5-5"
    assert line["input_tokens"] == 10
    assert line["output_tokens"] == 5
    assert "cost_usd" in line
    assert "latency_s" in line


def test_count_tokens_needs_no_api_key_either(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = FakeMessagesClient(fake_response(), token_count=42)

    n = count_tokens([{"role": "user", "content": "hi"}], client=client)

    assert n == 42
    [sent] = client.count_tokens_calls
    assert sent["model"] == "claude-sonnet-5-5"
