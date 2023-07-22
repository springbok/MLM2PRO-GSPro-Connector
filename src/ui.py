import logging
from dataclasses import dataclass

@dataclass
class Color:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'

class UI:
    @staticmethod
    def display_message(color, prefix, message):
        print(f"{color}{prefix}{Color.RESET}", message)
        if color == Color.RED:
            logging.error(message)
        else:
            logging.info(message)




