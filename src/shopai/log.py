"""Structured logging: every log call prints one JSON line to stdout."""

import logging

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Set up logging for the whole program. Call once, at startup, never on import."""
    structlog.configure(
        # Each processor adds to the event dict in turn; the last one turns it into JSON.
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.format_exc_info,  # log.exception() adds the traceback
            structlog.processors.JSONRenderer(),
        ],
        # Calls below `level` are dropped before any processor runs.
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelNamesMapping()[level]),
        logger_factory=structlog.PrintLoggerFactory(),
    )


def get_logger(name: str) -> structlog.typing.FilteringBoundLogger:
    """A logger that adds `module=<name>` to every line it writes."""
    # Stays lazy until first use, so a module-level logger still picks up
    # the configuration that main() sets later. (The field can't be called
    # `logger`: structlog already uses that name for its own argument.)
    return structlog.get_logger(module=name)
