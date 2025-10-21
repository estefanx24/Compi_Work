
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set
from scanner import lex
from tok import Token
from ast_nodes import *  # AST nodes

Symbol = str

@dataclass(frozen=True)
class Production:
    head: Symbol
    body: Tuple[Symbol, ...]
    idx: int

@dataclass(frozen=True)
class Item:
    prod_idx: int
    dot: int
    look: Symbol

@dataclass
class Grammar:
    start: Symbol
    prods: List[Production]
    terminals: Set[Symbol]
    nonterminals: Set[Symbol]
    first_cache: Dict[Tuple[Symbol, ...], Set[Symbol]] = field(default_factory=dict)

    @staticmethod
    def from_rules(start: Symbol, rules: Dict[Symbol, List[List[Symbol]]], terminals: Set[Symbol]):
        prods = []
        nonterminals = set(rules.keys())
        idx = 0
        for H, alts in rules.items():
            for rhs in alts:
                prods.append(Production(H, tuple(rhs), idx)); idx += 1
        return Grammar(start, prods, set(terminals), nonterminals)

    def prods_by_head(self, H: Symbol) -> List[Production]:
        return [p for p in self.prods if p.head == H]

    def first_of_seq(self, seq: Tuple[Symbol, ...]) -> Set[Symbol]:
        if seq in self.first_cache:
            return self.first_cache[seq]
        out: Set[Symbol] = set()
        if not seq:
            out.add("ε")
        else:
            for s in seq:
                if s in self.terminals:
                    out.add(s); break
                else:
                    f = set()
                    for p in self.prods_by_head(s):
                        f |= self.first_of_seq(p.body) - {"ε"}
                    out |= f
                    if "ε" not in f:
                        break
            else:
                out.add("ε")
        self.first_cache[seq] = out
        return out

def closure(items: Set[Item], G: Grammar) -> Set[Item]:
    C = set(items); changed = True
    while changed:
        changed = False; to_add = set()
        for it in C:
            p = G.prods[it.prod_idx]
            if it.dot < len(p.body):
                B = p.body[it.dot]
                if B in G.nonterminals:
                    beta_a = p.body[it.dot+1:] + (it.look,)
                    lookaheads = G.first_of_seq(beta_a) - {"ε"}
                    for q in G.prods_by_head(B):
                        for a in lookaheads:
                            cand = Item(q.idx, 0, a)
                            if cand not in C: to_add.add(cand)
        if to_add:
            C |= to_add; changed = True
    return C

def goto(I: Set[Item], X: Symbol, G: Grammar) -> Set[Item]:
    J = set()
    for it in I:
        p = G.prods[it.prod_idx]
        if it.dot < len(p.body) and p.body[it.dot] == X:
            J.add(Item(it.prod_idx, it.dot+1, it.look))
    return closure(J, G) if J else set()

def canonical_collection(G: Grammar) -> List[Set[Item]]:
    start_aug = Production(G.start+"'", (G.start,), len(G.prods))
    G.prods.append(start_aug)
    I0 = closure({Item(start_aug.idx, 0, "$")}, G)
    C = [I0]
    symbols = list(G.terminals | G.nonterminals)
    changed = True
    while changed:
        changed = False
        for I in list(C):
            for X in symbols:
                J = goto(I, X, G)
                if J and all(J != K for K in C):
                    C.append(J); changed = True
    return C

def build_tables(G: Grammar):
    states = canonical_collection(G)
    state_index = {frozenset(s): i for i, s in enumerate(states)}
    ACTION: Dict[Tuple[int, Symbol], Tuple[str, int]] = {}
    GOTO: Dict[Tuple[int, Symbol], int] = {}
    for i, I in enumerate(states):
        for it in I:
            p = G.prods[it.prod_idx]
            if it.dot < len(p.body):
                a = p.body[it.dot]
                J = goto(I, a, G)
                if a in G.terminals:
                    if J: ACTION[(i, a)] = ("shift", state_index[frozenset(J)])
                else:
                    if J: GOTO[(i, a)] = state_index[frozenset(J)]
            else:
                if p.head == G.start+"'" and it.look == "$":
                    ACTION[(i, "$")] = ("accept", 0)
                else:
                    ACTION[(i, it.look)] = ("reduce", p.idx)
    return states, ACTION, GOTO

class LRParser:
    def __init__(self, ACTION, GOTO, productions, semantica):
        self.ACTION = ACTION; self.GOTO = GOTO
        self.productions = productions; self.semantica = semantica

    def parse(self, code: str):
        tokens = list(lex(code))
        pos = 0; stack_states = [0]; stack_vals = []
        def ttype(i): return tokens[i].type if i < len(tokens) else "$"
        while True:
            s = stack_states[-1]; a = ttype(pos)
            act = self.ACTION.get((s, a))
            if act is None:
                raise SyntaxError(f"Error de parseo en estado {s} con token {a} @pos {tokens[pos].pos if pos < len(tokens) else 'EOF'}")
            kind, arg = act
            if kind == "shift":
                stack_states.append(arg); stack_vals.append(tokens[pos]); pos += 1
            elif kind == "reduce":
                head, body = self.productions[arg]; n = len(body)
                rhs_vals = stack_vals[-n:] if n else []
                if n: del stack_vals[-n:]; del stack_states[-n:]
                node = self.semantica[arg](rhs_vals)
                stack_vals.append(node)
                s2 = stack_states[-1]
                g = self.GOTO.get((s2, head))
                if g is None: raise SyntaxError("Tabla GOTO incompleta")
                stack_states.append(g)
            elif kind == "accept":
                assert len(stack_vals) == 1; return stack_vals[0]

# Gramática
terminals = {
    "ID","NUM","PRINT","IF","THEN","ELSE","ENDIF","WHILE","DO","ENDWHILE",
    "LPAREN","RPAREN","PLUS","MINUS","MUL","DIV","POW","SQRT","ASSIGN","SEMICOL"
}
rules = {
    "program": [["stmts"]],
    "stmts":   [["stmts","SEMICOL","stm"], ["stm"]],
    "stm":     [["ID","ASSIGN","exp"],
                ["PRINT","LPAREN","exp","RPAREN"],
                ["IF","exp","THEN","stmts","ELSE","stmts","ENDIF"],
                ["WHILE","exp","DO","stmts","ENDWHILE"]],
    "exp":     [["exp","PLUS","term"],
                ["exp","MINUS","term"],
                ["term"]],
    "term":    [["term","MUL","pow"],
                ["term","DIV","pow"],
                ["pow"]],
    "pow":     [["factor","POW","factor"],["factor"]],
    "factor":  [["NUM"],["ID"],["SQRT","LPAREN","exp","RPAREN"],["LPAREN","exp","RPAREN"]],
}
G = Grammar.from_rules("program", rules, terminals)
states, ACTION, GOTO = build_tables(G)
productions = [(p.head, p.body) for p in G.prods]

def SEM_builder():
    M = {}
    for idx,(h,b) in enumerate(productions):
        if (h,b)==("program",("stmts",)):                  M[idx] = lambda v: Program(v[0])
        elif (h,b)==("stmts",("stmts","SEMICOL","stm")):   M[idx] = lambda v: v[0]+[v[2]]
        elif (h,b)==("stmts",("stm",)):                    M[idx] = lambda v: [v[0]]
        elif (h,b)==("stm",("ID","ASSIGN","exp")):         M[idx] = lambda v: Assign(v[0].value, v[2])
        elif (h,b)==("stm",("PRINT","LPAREN","exp","RPAREN")): M[idx] = lambda v: Print(v[2])
        elif (h,b)==("stm",("IF","exp","THEN","stmts","ELSE","stmts","ENDIF")): M[idx] = lambda v: If(v[1], v[3], v[5])
        elif (h,b)==("stm",("WHILE","exp","DO","stmts","ENDWHILE")): M[idx] = lambda v: While(v[1], v[3])
        elif (h,b)==("exp",("exp","PLUS","term")):         M[idx] = lambda v: BinOp("+", v[0], v[2])
        elif (h,b)==("exp",("exp","MINUS","term")):        M[idx] = lambda v: BinOp("-", v[0], v[2])
        elif (h,b)==("exp",("term",)):                     M[idx] = lambda v: v[0]
        elif (h,b)==("term",("term","MUL","pow")):         M[idx] = lambda v: BinOp("*", v[0], v[2])
        elif (h,b)==("term",("term","DIV","pow")):         M[idx] = lambda v: BinOp("/", v[0], v[2])
        elif (h,b)==("term",("pow",)):                     M[idx] = lambda v: v[0]
        elif (h,b)==("pow",("factor","POW","factor")):     M[idx] = lambda v: BinOp("**", v[0], v[2])
        elif (h,b)==("pow",("factor",)):                   M[idx] = lambda v: v[0]
        elif (h,b)==("factor",("NUM",)):                   M[idx] = lambda v: Number(int(v[0].value))
        elif (h,b)==("factor",("ID",)):                    M[idx] = lambda v: Id(v[0].value)
        elif (h,b)==("factor",("SQRT","LPAREN","exp","RPAREN")): M[idx] = lambda v: Sqrt(v[2])
        elif (h,b)==("factor",("LPAREN","exp","RPAREN")):  M[idx] = lambda v: v[1]
        else:                                              M[idx] = lambda v: None
    return M

SEM = SEM_builder()

def build_parser():
    return LRParser(ACTION, GOTO, productions, SEM), states, ACTION, GOTO
