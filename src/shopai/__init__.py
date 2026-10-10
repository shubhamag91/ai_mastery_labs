from importlib.metadata import version

from shopai.config import get_settings
from shopai.log import configure_logging, get_logger


def main() -> None:
    """Start-up routine for the `shopai` command: load settings, then set up logging."""
    settings = get_settings()  # fails fast here if a setting is missing or invalid
    configure_logging(settings.log_level)

    log = get_logger(__name__)
    log.debug("settings_loaded", environment=settings.environment, log_level=settings.log_level)
    log.info("startup", version=version("shopai"), environment=settings.environment)
