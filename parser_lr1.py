# parser_lr1.py — LR(1) canónico con tablas ACTION/GOTO y simulación
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Set, Dict, Iterable
import pandas as pd

EPS = "ε"
END = "$"

# -----------------------------
# Lectura de gramática (texto)
# -----------------------------
def parse_grammar_text(gram_text: str):
    """
    Formato por línea:
        A -> α1 | α2 | ...   (usa 'ε' para vacío)
    """
    lines = [ln.strip() for ln in gram_text.strip().splitlines() if ln.strip()]
    prods: List[Tuple[str, List[str]]] = []
    heads = []
    for line in lines:
        left, right = line.split("->")
        left = left.strip()
        heads.append(left)
        for alt in right.split("|"):
            body = alt.strip().split()
            if body == [EPS]:  # epsilon
                body = []
            prods.append((left, body))
    start = heads[0]
    nonterminals = {h for h,_ in prods}
    symbols_in_bodies = {s for _,b in prods for s in b}
    terminals = {s for s in symbols_in_bodies if s not in nonterminals}
    return prods, start, nonterminals, terminals

# -----------------------------
# FIRST por símbolo (con $)
# -----------------------------
def first_sets(nonterminals: Set[str], terminals: Set[str], prods: List[Tuple[str, List[str]]]):
    # IMPORTANTE: incluir END ($) como símbolo con FIRST($) = {$}
    symbols = set(nonterminals) | set(terminals) | {END}
    FIRST: Dict[str, Set[str]] = {X: set() for X in symbols}
    for t in set(terminals) | {END}:
        FIRST[t].add(t)
    changed = True
    while changed:
        changed = False
        for A, alpha in prods:
            if not alpha:
                if EPS not in FIRST[A]:
                    FIRST[A].add(EPS); changed = True
                continue
            acc = set()
            for s in alpha:
                acc |= (FIRST[s] - {EPS})
                if EPS not in FIRST[s]:
                    break
            else:
                acc.add(EPS)
            old = len(FIRST[A])
            FIRST[A] |= acc
            if len(FIRST[A]) != old:
                changed = True
    return FIRST

def first_of_seq(seq: Iterable[str], FIRST: Dict[str, Set[str]]):
    out = set()
    for s in seq:
        if s == END:  # blindaje para lookahead $
            out.add(END)
            break
        fs = FIRST[s]
        out |= (fs - {EPS})
        if EPS not in fs:
            break
    else:
        out.add(EPS)
    return out

# -----------------------------
# Aumentar gramática
# -----------------------------
def augment(prods: List[Tuple[str, List[str]]], start: str):
    """
    Si ya te pasan S' -> S como PRIMERA producción, no volvemos a aumentar.
    """
    if prods and len(prods[0][1]) == 1 and prods[0][0].endswith("'") and prods[0][1][0] == start:
        return list(prods), prods[0][0]
    S_ = f"{start}'"
    return prods + [(S_, [start])], S_

def prods_by_head(prods):
    mp = defaultdict(list)
    for i,(H,B) in enumerate(prods):
        mp[H].append((i,H,B))
    return mp

# -----------------------------
# Items LR(1), CLOSURE y GOTO
# -----------------------------
@dataclass(frozen=True)
class Item:
    prod_idx: int
    dot: int
    look: str

def closure(items: Set[Item], prods, by_head, FIRST, nonterminals: Set[str]):
    C = set(items)
    changed = True
    while changed:
        changed = False
        addQ = set()
        for it in C:
            pidx, dot, la = it.prod_idx, it.dot, it.look
            H,B = prods[pidx]
            if dot < len(B):
                X = B[dot]
                if X in nonterminals:
                    beta_a = B[dot+1:] + [la]
                    looks = first_of_seq(beta_a, FIRST)
                    for (qidx,_,qB) in by_head[X]:
                        for a in looks:
                            newi = Item(qidx, 0, a)
                            if newi not in C:
                                addQ.add(newi)
        if addQ:
            C |= addQ; changed = True
    return C

def goto(I: Set[Item], X: str, prods):
    J = set()
    for it in I:
        pidx, dot, la = it.prod_idx, it.dot, it.look
        H,B = prods[pidx]
        if dot < len(B) and B[dot] == X:
            J.add(Item(pidx, dot+1, la))
    return J

def canonical_collection(prods, start, FIRST, terminals, nonterminals):
    aug, S_ = augment(prods, start)
    by_head = prods_by_head(aug)
    I0 = closure({Item(len(aug)-1, 0, END)}, aug, by_head, FIRST, nonterminals | {S_})
    C = [I0]
    index = {frozenset(I0): 0}
    symbols = sorted(terminals | nonterminals)
    changed = True
    while changed:
        changed = False
        for I in list(C):
            for X in symbols:
                base = goto(I, X, aug)
                if not base:
                    continue
                J = closure(base, aug, by_head, FIRST, nonterminals | {S_})
                fJ = frozenset(J)
                if fJ not in index:
                    index[fJ] = len(C)
                    C.append(J); changed = True
    return C, index, aug, S_

# -----------------------------
# Tablas ACTION / GOTO
# -----------------------------
def build_tables(prods, start, terminals, nonterminals, FIRST):
    C, index, aug, S_ = canonical_collection(prods, start, FIRST, terminals, nonterminals)
    ACTION: Dict[tuple, tuple] = {}
    GOTO: Dict[tuple, int] = {}
    conflicts = []

    def add_action(k, v):
        if k in ACTION and ACTION[k] != v:
            conflicts.append(f"Conflicto en ACTION{k}: {ACTION[k]} vs {v}")
        ACTION[k] = v

    by_head = prods_by_head(aug)
    for i, I in enumerate(C):
        for it in I:
            pidx, dot, la = it.prod_idx, it.dot, it.look
            H,B = aug[pidx]
            if dot < len(B):
                a = B[dot]
                base = goto(I, a, aug)
                if a in terminals and base:
                    J = closure(base, aug, by_head, FIRST, nonterminals | {S_})
                    j = index[frozenset(J)]
                    add_action((i, a), ('shift', j))
                elif a in nonterminals and base:
                    J = closure(base, aug, by_head, FIRST, nonterminals | {S_})
                    j = index[frozenset(J)]
                    GOTO[(i, a)] = j
            else:
                if H == S_ and la == END:
                    add_action((i, END), ('accept', 0))
                else:
                    add_action((i, la), ('reduce', pidx))
    return ACTION, GOTO, C, aug, conflicts

# -----------------------------
# Helpers para UI/tablas/trace
# -----------------------------
def action_table_df(ACTION, terminals, nstates):
    rows = []
    cols = sorted(list(terminals)) + [END]
    for s in range(nstates):
        row = {"state": s}
        for t in cols:
            act = ACTION.get((s,t))
            if not act:
                row[t] = ""
            else:
                k, a = act
                if k == "shift": row[t] = f"s{a}"
                elif k == "reduce": row[t] = f"r{a}"
                else: row[t] = "acc"
        rows.append(row)
    return pd.DataFrame(rows).set_index("state")

def goto_table_df(G, nonterminals, nstates):
    rows = []
    cols = sorted(list(nonterminals))
    for s in range(nstates):
        row = {"state": s}
        for A in cols:
            row[A] = G.get((s,A), "")
        rows.append(row)
    return pd.DataFrame(rows).set_index("state")

def states_to_str(states, aug):
    blocks = []
    for i, I in enumerate(states):
        lines = []
        for it in sorted(I, key=lambda x:(x.prod_idx, x.dot, x.look)):
            H,B = aug[it.prod_idx]
            body = list(B)
            body.insert(it.dot, "•")
            rhs = " ".join(body) if body else "•"
            lines.append(f"I{i}: [{H} → {rhs}, {it.look}]")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)

def analizar_cadena_lr(input_str: str, ACTION, GOTO, aug, start):
    tokens = input_str.strip().split() + [END]
    pos = 0
    st_states = [0]
    st_syms = []
    frames = []

    def a(): return tokens[pos]

    while True:
        s = st_states[-1]
        act = ACTION.get((s, a()))
        stack_show = f"{' '.join(map(str, st_states))} || {' '.join(st_syms)}"
        inp_show = " ".join(tokens[pos:])
        if act is None:
            frames.append((stack_show, inp_show, f"Error: no ACTION[{s}, {a()}]"))
            frames.append(("", "", "CADENA NO VÁLIDA"))
            break
        kind, arg = act
        if kind == "shift":
            frames.append((stack_show, inp_show, f"shift -> s{arg}"))
            st_states.append(arg); st_syms.append(a()); pos += 1
        elif kind == "reduce":
            H,B = aug[arg]
            k = len(B)
            if k:
                st_states = st_states[:-k]
                st_syms = st_syms[:-k]
            s2 = st_states[-1]
            g = GOTO.get((s2, H))
            if g is None:
                frames.append((stack_show, inp_show, f"Error: no GOTO[{s2}, {H}]"))
                frames.append(("", "", "CADENA NO VÁLIDA"))
                break
            st_states.append(g); st_syms.append(H)
            frames.append((stack_show, inp_show, f"reduce {H} → {' '.join(B) if B else EPS}; goto s{g}"))
        else:
            frames.append((stack_show, inp_show, "ACCEPT"))
            frames.append(("", "", "CADENA VÁLIDA"))
            break

    return pd.DataFrame(frames, columns=["Pila (estados || símbolos)", "Entrada", "Acción"])
