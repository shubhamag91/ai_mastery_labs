import json

import pytest
import structlog

from shopai.log import configure_logging, get_logger


@pytest.fixture(autouse=True)
def reset_structlog():
    # configure_logging() changes global state; put it back after each test.
    yield
    structlog.reset_defaults()


def read_lines(capsys):
    """Every line the test printed, parsed as JSON. Fails if any line isn't JSON."""
    return [json.loads(line) for line in capsys.readouterr().out.splitlines()]


def test_each_log_call_is_one_json_line(capsys):
    configure_logging("INFO")
    get_logger("shopai.test").info("rows_processed", rows=42)

    [line] = read_lines(capsys)
    assert line["event"] == "rows_processed"
    assert line["level"] == "info"
    assert line["module"] == "shopai.test"
    assert "timestamp" in line


def test_fields_keep_their_types(capsys):
    configure_logging("INFO")
    get_logger("shopai.test").info("llm_call", tokens=512, latency_s=2.3, cached=False)

    [line] = read_lines(capsys)
    assert line["tokens"] == 512
    assert line["latency_s"] == 2.3
    assert line["cached"] is False


def test_logger_created_before_configure_still_uses_it(capsys):
    log = get_logger("shopai.test")  # like a module-level logger, created at import time
    configure_logging("INFO")
    log.info("configured_later")

    [line] = read_lines(capsys)  # the default config prints plain text, so json.loads would fail
    assert line["event"] == "configured_later"


def test_debug_is_dropped_at_info_level(capsys):
    configure_logging("INFO")
    log = get_logger("shopai.test")
    log.debug("noisy_detail")
    log.info("kept")

    assert [line["event"] for line in read_lines(capsys)] == ["kept"]


def test_debug_is_kept_at_debug_level(capsys):
    configure_logging("DEBUG")
    get_logger("shopai.test").debug("noisy_detail")

    assert [line["event"] for line in read_lines(capsys)] == ["noisy_detail"]
