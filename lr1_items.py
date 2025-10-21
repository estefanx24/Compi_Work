# lr1_items.py — Items LR(1), CLOSURE y GOTO
from dataclasses import dataclass
from typing import Set
from grammar import first_of_seq, END


@dataclass(frozen=True)
class Item:
    """Item LR(1): [A → α•β, a]"""
    prod_idx: int
    dot: int
    look: str


def closure(items: Set[Item], prods, by_head, FIRST, nonterminals: Set[str]):
    """Calcula la clausura de un conjunto de items LR(1)."""
    C = set(items)
    changed = True
    while changed:
        changed = False
        addQ = set()
        for it in C:
            pidx, dot, la = it.prod_idx, it.dot, it.look
            H, B = prods[pidx]
            if dot < len(B):
                X = B[dot]
                if X in nonterminals:
                    beta_a = B[dot + 1:] + [la]
                    looks = first_of_seq(beta_a, FIRST)
                    for (qidx, _, qB) in by_head[X]:
                        for a in looks:
                            newi = Item(qidx, 0, a)
                            if newi not in C:
                                addQ.add(newi)
        if addQ:
            C |= addQ
            changed = True
    return C


def goto(I: Set[Item], X: str, prods):
    """Calcula GOTO(I, X): mueve el punto sobre el símbolo X."""
    J = set()
    for it in I:
        pidx, dot, la = it.prod_idx, it.dot, it.look
        H, B = prods[pidx]
        if dot < len(B) and B[dot] == X:
            J.add(Item(pidx, dot + 1, la))
    return J


def canonical_collection(prods, start, FIRST, terminals, nonterminals):
    """Construye la colección canónica de conjuntos de items LR(1)."""
    from grammar import augment, prods_by_head

    aug, S_ = augment(prods, start)
    by_head = prods_by_head(aug)
    I0 = closure({Item(len(aug) - 1, 0, END)}, aug, by_head, FIRST, nonterminals | {S_})
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
                    C.append(J)
                    changed = True
    return C, index, aug, S_