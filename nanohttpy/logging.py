import logging

logger = logging.Logger("nanohttpy")

logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

__logger_formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d | %(name)-12s | %(levelname)-8s | %(message)s",
    "%Y-%m-%d %H:%M:%S",
)
for h in logger.handlers:
    h.setFormatter(__logger_formatter)

print("Coucou")
