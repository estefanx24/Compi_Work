
import re
from typing import Iterator
from tok import Token, TOK, KEYWORDS

RE_NUM = re.compile(r"\d+")
RE_ID  = re.compile(r"[A-Za-z_]\w*")
RE_WS  = re.compile(r"[ \t\r\n]+")

TOK_PATTERNS = [
    ("POW",      re.compile(r"\*\*")),
    ("LE",       re.compile(r"<")),
    ("PLUS",     re.compile(r"\+")),
    ("MINUS",    re.compile(r"-")),
    ("MUL",      re.compile(r"\*")),
    ("DIV",      re.compile(r"/")),
    ("LPAREN",   re.compile(r"\(")),
    ("RPAREN",   re.compile(r"\)")),
    ("ASSIGN",   re.compile(r"=")),
    ("SEMICOL",  re.compile(r";")),
]

def lex(code: str) -> Iterator[Token]:
    i, n = 0, len(code)
    while i < n:
        m = RE_WS.match(code, i)
        if m:
            i = m.end()
            continue
        m = RE_NUM.match(code, i)
        if m:
            yield Token("NUM", m.group(0), i); i = m.end(); continue
        m = RE_ID.match(code, i)
        if m:
            text = m.group(0)
            ttype = KEYWORDS.get(text, "ID")
            yield Token(ttype, text, i); i = m.end(); continue
        for name, rx in TOK_PATTERNS:
            m = rx.match(code, i)
            if m:
                yield Token(name, m.group(0), i); i = m.end(); break
        else:
            raise SyntaxError(f"Caracter inesperado '{code[i]}' en {i}")
    yield Token("$", "$", n)
