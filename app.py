# app.py — Interfaz Streamlit para LR(1)
import streamlit as st
import pandas as pd
from parser_lr1 import (
    parse_grammar_text, first_sets, build_tables,
    action_table_df, goto_table_df, states_to_str, analizar_cadena_lr, EPS
)

st.set_page_config(page_title="LR(1) Visualizer", layout="wide")
st.title("🧭 Analizador LR(1) (canónico) — estilo jsMachines")

st.markdown("Pega tu gramática (usa **ε** para vacío). La app construye LR(1) canónico, muestra **ACTION/GOTO**, los **items** por estado y la **traza** paso a paso.")

default_grammar = """S -> C C
C -> c C | d"""

gram_text = st.text_area("📘 Gramática", value=default_grammar, height=160)
input_str = st.text_input("✍️ Cadena (tokens separados por espacio)", "c c d d")

if st.button("Construir LR(1) y simular"):
    try:
        prods, start, nonterminals, terminals = parse_grammar_text(gram_text)
        FIRST = first_sets(nonterminals, terminals, prods)
        ACTION, GOTO, states, augmented, conflicts = build_tables(prods, start, terminals, nonterminals, FIRST)

        st.success(f"Estados: **{len(states)}** | No terminales: {len(nonterminals)} | Terminales: {len(terminals)}")
        if conflicts:
            st.warning("⚠️ Conflictos detectados:")
            for c in conflicts: st.write("- ", c)

        with st.expander("📜 Producciones"):
            st.code("\n".join(f"{A} → {' '.join(B) if B else EPS}" for A,B in prods), language="bnf")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("ACTION")
            st.dataframe(action_table_df(ACTION, terminals, len(states)))
        with c2:
            st.subheader("GOTO")
            st.dataframe(goto_table_df(GOTO, nonterminals, len(states)))

        with st.expander("🔎 Items por estado"):
            st.code(states_to_str(states, augmented))

        st.subheader("🧾 Traza LR(1)")
        df = analizar_cadena_lr(input_str, ACTION, GOTO, augmented, start)
        st.dataframe(df)

    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption("Ejemplo típico: S→CC; C→cC|d  ⇒ acepta cadenas de la forma c^i d c^j d.")
