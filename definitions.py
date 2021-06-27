from pathlib import Path
from logger import log

BASE_DIR = Path(__file__).resolve().parent


def playerselected(func):
    def wrapper(self, *args, **kwargs):
        if self.player is None:
            log.warning(f"A player must be selected to run method '{func.__name__}()'")
            return None
        else:
            return func(self, *args, **kwargs)

    return wrapper