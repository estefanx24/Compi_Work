# parser_analyzer.py — Análisis sintáctico de cadenas (con y sin árbol)
import pandas as pd
from typing import List, Tuple, Optional
from grammar import EPS, END
from parse_tree import PTNode


def analizar_cadena_lr(input_str: str, ACTION, GOTO, aug, start):
    """
    Realiza el análisis sintáctico LR(1) de una cadena de entrada.
    Retorna un DataFrame con la traza del análisis.
    """
    tokens = input_str.strip().split() + [END]
    pos = 0
    st_states = [0]
    st_syms = []
    frames = []

    def a():
        return tokens[pos]

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
            st_states.append(arg)
            st_syms.append(a())
            pos += 1
        elif kind == "reduce":
            H, B = aug[arg]
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
            st_states.append(g)
            st_syms.append(H)
            frames.append((stack_show, inp_show, f"reduce {H} → {' '.join(B) if B else EPS}; goto s{g}"))
        else:  # accept
            frames.append((stack_show, inp_show, "ACCEPT"))
            frames.append(("", "", "CADENA VÁLIDA"))
            break

    return pd.DataFrame(frames, columns=["Pila (estados || símbolos)", "Entrada", "Acción"])


def analizar_cadena_lr_con_arbol(input_str: str, ACTION, GOTO, aug, start) -> Tuple[pd.DataFrame, Optional[PTNode]]:
    """
    Análisis sintáctico LR(1) con construcción del árbol de derivación.

    - shift: apila un nodo terminal con el lexema
    - reduce A->β: crea nodo A con hijos β (en orden), lo apila
    - ε: nodo A sin hijos

    Args:
        input_str: Cadena de entrada a analizar
        ACTION: Tabla ACTION del parser
        GOTO: Tabla GOTO del parser
        aug: Gramática aumentada
        start: Símbolo inicial

    Returns:
        Tupla (traza_df, root) donde:
        - traza_df: DataFrame con la traza del análisis
        - root: Nodo raíz del árbol de derivación (None si hay error)
    """
    tokens = input_str.strip().split() + [END]
    pos = 0
    st_states = [0]
    st_syms: List[str] = []
    node_stack: List[PTNode] = []
    frames = []

    def a():
        return tokens[pos]

    while True:
        s = st_states[-1]
        act = ACTION.get((s, a()))
        stack_show = f"{' '.join(map(str, st_states))} || {' '.join(st_syms)}"
        inp_show = " ".join(tokens[pos:])

        if act is None:
            frames.append((stack_show, inp_show, f"Error: no ACTION[{s}, {a()}]"))
            frames.append(("", "", "CADENA NO VÁLIDA"))
            return pd.DataFrame(frames, columns=["Pila (estados || símbolos)", "Entrada", "Acción"]), None

        kind, arg = act
        if kind == "shift":
            # Crear nodo terminal
            term_node = PTNode(label=a(), children=[])
            node_stack.append(term_node)
            frames.append((stack_show, inp_show, f"shift -> s{arg}"))
            st_states.append(arg)
            st_syms.append(a())
            pos += 1

        elif kind == "reduce":
            H, B = aug[arg]
            k = len(B)
            # Extraer hijos: pop k nodos (en orden de aparición)
            children = []
            if k:
                # Los nodos extraídos están en orden correcto (últimos k)
                children = node_stack[-k:]
                node_stack = node_stack[:-k]
                st_states = st_states[:-k]
                st_syms = st_syms[:-k]

            # Crear nodo de no terminal H con hijos en el orden correcto
            new_node = PTNode(label=H, children=list(children))
            node_stack.append(new_node)

            s2 = st_states[-1]
            g = GOTO.get((s2, H))
            if g is None:
                frames.append((stack_show, inp_show, f"Error: no GOTO[{s2}, {H}]"))
                frames.append(("", "", "CADENA NO VÁLIDA"))
                return pd.DataFrame(frames, columns=["Pila (estados || símbolos)", "Entrada", "Acción"]), None

            st_states.append(g)
            st_syms.append(H)
            frames.append((stack_show, inp_show, f"reduce {H} → {' '.join(B) if B else EPS}; goto s{g}"))

        else:  # accept
            frames.append((stack_show, inp_show, "ACCEPT"))
            frames.append(("", "", "CADENA VÁLIDA"))
            # Raíz: si la gramática aumentada es S'->S, la cima debe ser S
            root = node_stack[-1] if node_stack else None
            return pd.DataFrame(frames, columns=["Pila (estados || símbolos)", "Entrada", "Acción"]), root