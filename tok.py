
from dataclasses import dataclass

TOK = {
    "POW": "**",
    "LE": "<",
    "PLUS": "+",
    "MINUS": "-",
    "MUL": "*",
    "DIV": "/",
    "LPAREN": "(",
    "RPAREN": ")",
    "ASSIGN": "=",
    "SEMICOL": ";",
}

KEYWORDS = {
    "print": "PRINT",
    "if": "IF",
    "then": "THEN",
    "else": "ELSE",
    "endif": "ENDIF",
    "while": "WHILE",
    "do": "DO",
    "endwhile": "ENDWHILE",
    "sqrt": "SQRT",
}

@dataclass
class Token:
    type: str
    value: str
    pos: int
