import gettext
import logging
from pathlib import Path

from src.core.config import settings

logger = logging.getLogger(__name__)

_LOCALE_DIR = Path(__file__).resolve().parent.parent / "locales"

try:
    _translations = gettext.translation(
        "messages",
        localedir=_LOCALE_DIR,
        languages=[settings.LOCALE],
    )
except FileNotFoundError:
    logger.warning(
        "No compiled translations (.mo) for locale '%s'. "
        "Run: pybabel compile -d src/locales",
        settings.LOCALE,
    )
    _translations = gettext.NullTranslations()


def t(key: str, **kwargs: object) -> str:
    translated = _translations.gettext(key)
    if kwargs:
        return translated.format(**kwargs)
    return translated
