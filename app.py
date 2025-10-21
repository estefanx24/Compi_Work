# app.py — LR(1) con FIRST/FOLLOW, ACTION/GOTO, items, traza y árbol
import streamlit as st
import pandas as pd

try:
    from graphviz import Source
    HAS_GRAPHVIZ = True
except Exception:
    HAS_GRAPHVIZ = False

from parser_lr1 import (
    parse_grammar_text, first_sets, follow_sets, build_tables,
    first_follow_to_df, action_table_df, goto_table_df,
    states_to_str, analizar_cadena_lr_con_arbol, tree_to_dot, tree_to_pretty_text, EPS
)

st.set_page_config(page_title="LR(1) Visualizer", layout="wide")
st.title("🧭 Analizador LR(1)")

st.markdown("Pega tu gramática (usa **ε** para vacío). Se muestran **FIRST/FOLLOW**, **ACTION/GOTO**, **items**, la **traza** y el **árbol de derivación**.")

default_grammar = """S -> C C
C -> c C | d"""

gram_text = st.text_area("📘 Gramática", value=default_grammar, height=160)
input_str = st.text_input("✍️ Cadena (tokens separados por espacio)", "c c d d")

if st.button("Construir LR(1), simular y dibujar árbol"):
    try:
        prods, start, nonterminals, terminals = parse_grammar_text(gram_text)
        FIRST = first_sets(nonterminals, terminals, prods)
        FOLLOW = follow_sets(nonterminals, terminals, prods, start, FIRST)
        ACTION, GOTO, states, augmented, conflicts = build_tables(prods, start, terminals, nonterminals, FIRST)

        st.success(f"Estados: **{len(states)}** | No terminales: {len(nonterminals)} | Terminales: {len(terminals)}")
        if conflicts:
            st.warning("⚠️ Conflictos detectados:")
            for c in conflicts: st.write("- ", c)

        # FIRST / FOLLOW
        st.subheader("📚 FIRST y FOLLOW")
        ff_df = first_follow_to_df(FIRST, FOLLOW, nonterminals)
        st.dataframe(ff_df)

        # Producciones
        with st.expander("📜 Producciones"):
            st.code("\n".join(f"{A} → {' '.join(B) if B else EPS}" for A,B in prods), language="bnf")

        # ACTION / GOTO
        st.subheader("⚙️ Tablas ACTION y GOTO")
        c1, c2 = st.columns(2)
        with c1:
            st.caption("ACTION (terminales)")
            st.dataframe(action_table_df(ACTION, terminals, len(states)))
        with c2:
            st.caption("GOTO (no terminales)")
            st.dataframe(goto_table_df(GOTO, nonterminals, len(states)))

        # Estados (items)
        with st.expander("🔎 Items por estado"):
            st.code(states_to_str(states, augmented))

        # Simulación + Árbol
        st.subheader("🧾 Traza LR(1) y 🌳 Árbol de derivación")
        trace_df, root = analizar_cadena_lr_con_arbol(input_str, ACTION, GOTO, augmented, start)
        st.dataframe(trace_df)

        if root is not None:
            if HAS_GRAPHVIZ:
                dot = tree_to_dot(root)
                st.graphviz_chart(dot)
            else:
                st.info("No se encontró la librería Python `graphviz`. Mostrando árbol en texto:")
                st.code(tree_to_pretty_text(root))
        else:
            st.error("No se pudo construir el árbol (la cadena no fue aceptada o hubo un error).")

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Ejemplo: S→CC; C→cC|d  ⇒ acepta cadenas de la forma c^i d c^j d.")
