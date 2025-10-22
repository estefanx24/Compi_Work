from typing import Dict
from lr1_items import canonical_collection, closure, goto
from grammar import prods_by_head, END

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
            H, B = aug[pidx]
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
