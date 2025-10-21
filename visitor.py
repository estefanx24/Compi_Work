
import math
from ast_nodes import *  # noqa

class Interpreter:
    def __init__(self):
        self.env = {}
        self.out_lines = []

    def eval_exp(self, e: Exp):
        if isinstance(e, Number): return e.value
        if isinstance(e, Id): return self.env.get(e.name, 0)
        if isinstance(e, Sqrt): return int(math.sqrt(self.eval_exp(e.expr)))
        if isinstance(e, BinOp):
            a, b = self.eval_exp(e.left), self.eval_exp(e.right)
            if e.op == "+": return a + b
            if e.op == "-": return a - b
            if e.op == "*": return a * b
            if e.op == "/": return a // b if b != 0 else 0
            if e.op == "**": return a ** b
        raise RuntimeError("Expresión no soportada")

    def exec_stm(self, s: Stm):
        if isinstance(s, Assign): self.env[s.name] = self.eval_exp(s.expr)
        elif isinstance(s, Print): self.out_lines.append(str(self.eval_exp(s.expr)))
        elif isinstance(s, If):
            if self.eval_exp(s.cond): self.exec_block(s.then_stms)
            else: self.exec_block(s.else_stms or [])
        elif isinstance(s, While):
            while self.eval_exp(s.cond): self.exec_block(s.body)
        else: raise RuntimeError("Sentencia no soportada")

    def exec_block(self, stms):
        for st in stms:
            self.exec_stm(st)

    def run(self, program: Program) -> str:
        self.exec_block(program.stms)
        return "\n".join(self.out_lines)
