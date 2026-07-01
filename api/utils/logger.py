import logging

LOGGER_NAME = "MTG_AI_ANALYZER"


logger = logging.getLogger(LOGGER_NAME)

if not logger.handlers:

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    console = logging.StreamHandler()

    console.setFormatter(formatter)

    logger.addHandler(console)
