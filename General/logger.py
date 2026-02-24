import logging
import sys
from datetime import datetime


class Logger:
    """
    A centralized logger for the Bulk Sentiment Analyzer.
    Provides formatted console output for debugging Kafka streams and API requests.
    """

    def __init__(self, name: str = "SentimentAnalyzer"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self.logger.propagate = False

        # Check if handlers already exist to prevent duplicate logs
        if not self.logger.handlers:
            self.formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Console Handler
            self.console_handler = logging.StreamHandler(sys.stdout)
            self.console_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.console_handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)
