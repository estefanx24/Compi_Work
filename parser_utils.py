# parser_utils.py — Utilidades para visualización de tablas, estados y FIRST/FOLLOW
import pandas as pd
from typing import Dict, Set
from grammar import END


def first_follow_to_df(FIRST: Dict[str, Set[str]], FOLLOW: Dict[str, Set[str]], nonterminals: Set[str]):
    """Genera un DataFrame con los conjuntos FIRST y FOLLOW."""
    rows = []
    for A in sorted(nonterminals):
        rows.append({
            "Símbolo": A,
            "FIRST": ", ".join(sorted(FIRST.get(A, set()))),
            "FOLLOW": ", ".join(sorted(FOLLOW.get(A, set()))),
        })
    return pd.DataFrame(rows)


def action_table_df(ACTION, terminals, nstates):
    """Genera un DataFrame con la tabla ACTION."""
    rows = []
    cols = sorted(list(terminals)) + [END]
    for s in range(nstates):
        row = {"state": s}
        for t in cols:
            act = ACTION.get((s, t))
            if not act:
                row[t] = ""
            else:
                k, a = act
                if k == "shift":
                    row[t] = f"s{a}"
                elif k == "reduce":
                    row[t] = f"r{a}"
                else:
                    row[t] = "acc"
        rows.append(row)
    return pd.DataFrame(rows).set_index("state")


def goto_table_df(G, nonterminals, nstates):
    """Genera un DataFrame con la tabla GOTO."""
    rows = []
    cols = sorted(list(nonterminals))
    for s in range(nstates):
        row = {"state": s}
        for A in cols:
            row[A] = G.get((s, A), "")
        rows.append(row)
    return pd.DataFrame(rows).set_index("state")


def states_to_str(states, aug):
    """Convierte los estados LR(1) a una representación legible."""
    blocks = []
    for i, I in enumerate(states):
        lines = []
        for it in sorted(I, key=lambda x: (x.prod_idx, x.dot, x.look)):
            H, B = aug[it.prod_idx]
            body = list(B)
            body.insert(it.dot, "•")
            rhs = " ".join(body) if body else "•"
            lines.append(f"I{i}: [{H} → {rhs}, {it.look}]")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)