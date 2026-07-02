from http import HTTPStatus
from pathlib import Path

import uvicorn.logging
import yaml

from src.core.config import settings

responses = {status.value: status.phrase for status in HTTPStatus}


class LogColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DEBUG = "\033[94m"  # Синий
    INFO = "\033[92m"  # Зелёный
    WARNING = "\033[93m"  # Жёлтый
    ERROR = "\033[91m"  # Красный
    CRITICAL = "\033[95m"  # Фиолетовый


HTTP_COLORS = {
    "1": LogColors.DEBUG,
    "2": LogColors.INFO,
    "3": LogColors.WARNING,
    "4": LogColors.ERROR,
    "5": LogColors.CRITICAL,
}

COLORS = {
    "DEBUG": LogColors.DEBUG,
    "INFO": LogColors.INFO,
    "WARNING": LogColors.WARNING,
    "ERROR": LogColors.ERROR,
    "CRITICAL": LogColors.CRITICAL,
}

RESET_COLOR = "\033[0m"
BOLD = "\033[1m"


class LoggingFormatter(uvicorn.logging.DefaultFormatter):
    def format(self, record):
        levelname_color = COLORS.get(record.levelname, "")
        record.levelname = f"{levelname_color}{record.levelname}{RESET_COLOR}"
        return super().format(record)


class AccessLoggingFormatter(LoggingFormatter):
    def format(self, record):
        message = super().format(record)

        if '"' in message:
            start = message.find('"')
            end = message.find('"', start + 1)
            if start != -1 and end != -1:
                original = message[start : end + 1]
                bolded = f"{BOLD}{original}{RESET_COLOR}"
                message = message.replace(original, bolded)

        parts = message.split()
        if len(parts) > 2 and parts[-1].isdigit():
            status_code = parts[-1]
            status_color = HTTP_COLORS.get(status_code[0], "")
            status_name = responses.get(int(status_code), "Unknown")
            colored_status = f"{status_color}{status_code} {status_name}{RESET_COLOR}"
            message = colored_status.join(message.rsplit(status_code, 1))

        return message


def get_log_config() -> dict:
    yaml_path = Path(__file__).parent / "logging.yaml"

    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    log_level = settings.LOG_LEVEL.upper()

    config["root"]["level"] = log_level
    config["loggers"]["uvicorn.error"]["level"] = log_level
    config["loggers"]["uvicorn.access"]["level"] = log_level

    config["loggers"]["gunicorn.error"]["level"] = log_level
    config["loggers"]["gunicorn.access"]["level"] = log_level

    return config
