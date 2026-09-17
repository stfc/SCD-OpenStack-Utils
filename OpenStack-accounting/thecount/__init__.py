import logging
import os
import sys

FORMAT = "%(asctime)s %(levelname)-8s [%(process)d] %(name)s: %(message)s"
LOG_FP = "/var/log/thecount/thecount.log"

# Get log level from environment, defaulting to INFO
log_level_name = os.getenv("THECOUNT_LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Formatter
formatter = logging.Formatter(FORMAT)

# Log to stderr
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setLevel(log_level)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Log to file
if not os.path.exists(LOG_FP):
    logger.warning(
        "log filepath %s does not exist, logs aren't being stored...", LOG_FP
    )
else:
    file_handler = logging.FileHandler(LOG_FP)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
