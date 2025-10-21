# grammar.py — Manejo de gramáticas y cálculo de FIRST
from collections import defaultdict
from typing import List, Tuple, Set, Dict, Iterable

EPS = "ε"
END = "$"


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
    nonterminals = {h for h, _ in prods}
    symbols_in_bodies = {s for _, b in prods for s in b}
    terminals = {s for s in symbols_in_bodies if s not in nonterminals}
    return prods, start, nonterminals, terminals


def first_sets(nonterminals: Set[str], terminals: Set[str], prods: List[Tuple[str, List[str]]]):
    """Calcula los conjuntos FIRST para todos los símbolos."""
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
                    FIRST[A].add(EPS)
                    changed = True
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
    """Calcula FIRST de una secuencia de símbolos."""
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


def follow_sets(nonterminals: Set[str], terminals: Set[str], prods: List[Tuple[str, List[str]]], start: str, FIRST: Dict[str, Set[str]]):
    """Calcula los conjuntos FOLLOW para todos los no terminales."""
    FOLLOW: Dict[str, Set[str]] = {A: set() for A in nonterminals}
    FOLLOW[start].add(END)  # start incluye $

    changed = True
    while changed:
        changed = False
        for A, alpha in prods:
            n = len(alpha)
            for i, B in enumerate(alpha):
                if B in nonterminals:
                    beta = alpha[i+1:]
                    if beta:
                        first_beta = first_of_seq(beta, FIRST) - {EPS}
                        before = len(FOLLOW[B])
                        FOLLOW[B] |= first_beta
                        if len(FOLLOW[B]) != before:
                            changed = True
                        if EPS in first_of_seq(beta, FIRST):
                            before = len(FOLLOW[B])
                            FOLLOW[B] |= FOLLOW[A]
                            if len(FOLLOW[B]) != before:
                                changed = True
                    else:
                        before = len(FOLLOW[B])
                        FOLLOW[B] |= FOLLOW[A]
                        if len(FOLLOW[B]) != before:
                            changed = True
    return FOLLOW


def augment(prods: List[Tuple[str, List[str]]], start: str):
    """
    Aumenta la gramática con S' -> S si no está ya aumentada.
    """
    if prods and len(prods[0][1]) == 1 and prods[0][0].endswith("'") and prods[0][1][0] == start:
        return list(prods), prods[0][0]
    S_ = f"{start}'"
    return prods + [(S_, [start])], S_


def prods_by_head(prods):
    """Indexa las producciones por su cabeza."""
    mp = defaultdict(list)
    for i, (H, B) in enumerate(prods):
        mp[H].append((i, H, B))
    return mp