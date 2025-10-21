
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Exp: ...
@dataclass
class Number(Exp):
    value: int
@dataclass
class Id(Exp):
    name: str
@dataclass
class Sqrt(Exp):
    expr: Exp
@dataclass
class BinOp(Exp):
    op: str
    left: Exp
    right: Exp

@dataclass
class Stm: ...
@dataclass
class Assign(Stm):
    name: str
    expr: Exp
@dataclass
class Print(Stm):
    expr: Exp
@dataclass
class If(Stm):
    cond: Exp
    then_stms: List[Stm]
    else_stms: Optional[List[Stm]]
@dataclass
class While(Stm):
    cond: Exp
    body: List[Stm]

@dataclass
class Program:
    stms: List[Stm]
