from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def playerselected(func):
    def wrapper(self):
        if self.player is None:
            print(f"A player must be selected to run method '{func.__name__}()'")
            return None
        else:
            func(self)

    return wrapper