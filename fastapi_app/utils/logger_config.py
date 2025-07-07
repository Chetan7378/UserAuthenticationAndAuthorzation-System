# src/utils/logger_config.py
import logging
import sys

def setup_logging():
    """Configures global logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Silence overly verbose loggers if needed
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("ldap3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)