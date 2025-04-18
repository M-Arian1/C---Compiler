
from enum import Enum

class Token(Enum):
    NUM = "NUM"
    ID = "ID"
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"


