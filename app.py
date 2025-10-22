# app.py — LR(1) con FIRST/FOLLOW, ACTION/GOTO, items, traza y árbol
import streamlit as st
import pandas as pd

try:
    from graphviz import Source

    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

from parser_lr1 import (
    parse_grammar_text,
    first_sets,
    follow_sets,
    build_tables,
    first_follow_to_df,
    action_table_df,
    goto_table_df,
    states_to_str,
    analizar_cadena_lr_con_arbol,
    tree_to_dot,
    tree_to_pretty_text,
    EPS,
    END
)

# Configuración de la página
st.set_page_config(
    page_title="LR(1) Visualizer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo personalizado
st.markdown(
    """
    <style>
        body {
            background-color: #1e1e1e; /* Fondo gris oscuro premium */
            color: #f5f5f5; /* Texto blanco suave */
        }
        .streamlit-expanderHeader {
            color: #f7a600; /* Color dorado para los encabezados */
        }
        .stButton>button {
            background-color: #f7a600; /* Botón dorado */
            color: white; /* Texto blanco en los botones */
            border-radius: 8px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #f5a300; /* Hover dorado más oscuro */
        }
        .css-1d391kg { /* Sidebar */
            background-color: #262626; /* Sidebar gris oscuro */
        }
        .css-1d391kg .css-1v0mbdj { /* Titulo del sidebar */
            color: #f7a600;
        }
        .stTextInput>div>div>input {
            background-color: #333333; /* Fondo oscuro para entradas de texto */
            color: #f5f5f5; /* Texto claro en entradas */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧭 Analizador LR(1)")
st.markdown(""" 
Analizador sintáctico **LR(1) canónico** con visualización completa:
- Conjuntos **FIRST** y **FOLLOW**
- Tablas **ACTION** y **GOTO**
- **Items LR(1)** por estado
- **Traza** de ejecución paso a paso
- **Árbol de derivación** gráfico

> 💡 Usa **ε** para producciones vacías
""")

# Ejemplos predefinidos
EXAMPLES = {
    "Gramática simple (S → CC)": """S -> C C
C -> c C | d""",
    "Expresiones aritméticas": """E -> E + T | T
T -> T * F | F
F -> ( E ) | id""",
    "Paréntesis balanceados": """S -> ( S ) | ε""",
    "if-then-else": """S -> i E t S | i E t S e S | a
E -> b"""
}

# Sidebar con opciones
with st.sidebar:
    st.header("⚙️ Configuración")
    selected_example = st.selectbox(
        "Ejemplos predefinidos:",
        options=["Personalizado"] + list(EXAMPLES.keys())
    )

    show_states = st.checkbox("Mostrar items LR(1)", value=False)
    show_productions = st.checkbox("Mostrar producciones", value=False)

# Gramática de entrada
if selected_example != "Personalizado":
    default_grammar = EXAMPLES[selected_example]
else:
    default_grammar = """S -> C C
C -> c C | d"""

gram_text = st.text_area(
    "📘 Gramática",
    value=default_grammar,
    height=160,
    help="Formato: A -> α1 | α2 | ... (usa ε para producción vacía)"
)

# Entrada
input_str = st.text_input(
    "✍️ Cadena de entrada",
    "c c d d",
    help="Tokens separados por espacio"
)

# Botón principal
if st.button("🚀 Analizar", type="primary"):
    if not gram_text.strip():
        st.error("❌ La gramática no puede estar vacía")
    elif not input_str.strip():
        st.error("❌ La cadena de entrada no puede estar vacía")
    else:
        try:
            # Parsing de gramática
            with st.spinner("Construyendo parser LR(1)..."):
                prods, start, nonterminals, terminals = parse_grammar_text(gram_text)
                FIRST = first_sets(nonterminals, terminals, prods)
                FOLLOW = follow_sets(nonterminals, terminals, prods, start, FIRST)
                ACTION, GOTO, states, augmented, conflicts = build_tables(
                    prods, start, terminals, nonterminals, FIRST
                )

            # Información general
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Estados", len(states))
            with col2:
                st.metric("No terminales", len(nonterminals))
            with col3:
                st.metric("Terminales", len(terminals))
            with col4:
                st.metric("Producciones", len(prods))

            # Conflictos
            if conflicts:
                st.warning("⚠️ **Conflictos detectados:**")
                for c in conflicts:
                    st.write(f"- {c}")
            else:
                st.success("✅ Gramática LR(1) válida (sin conflictos)")

            # FIRST / FOLLOW
            st.subheader("📚 Conjuntos FIRST y FOLLOW")
            ff_df = first_follow_to_df(FIRST, FOLLOW, nonterminals)
            st.dataframe(ff_df, use_container_width=True)

            # Producciones (opcional)
            if show_productions:
                with st.expander("📜 Producciones de la gramática"):
                    prod_text = "\n".join(
                        f"{i}: {A} → {' '.join(B) if B else EPS}"
                        for i, (A, B) in enumerate(prods)
                    )
                    st.code(prod_text, language="bnf")

            # ACTION / GOTO
            st.subheader("⚙️ Tablas ACTION y GOTO")
            c1, c2 = st.columns([3, 2])
            with c1:
                st.caption("**ACTION** (terminales)")
                act_df = action_table_df(ACTION, terminals, len(states))
                st.dataframe(act_df, use_container_width=True)
            with c2:
                st.caption("**GOTO** (no terminales)")
                goto_df = goto_table_df(GOTO, nonterminals, len(states))
                st.dataframe(goto_df, use_container_width=True)

            # Estados (items) - opcional
            if show_states:
                with st.expander("🔎 Items LR(1) por estado"):
                    st.code(states_to_str(states, augmented))

            # Simulación + Árbol
            st.subheader("🧾 Analizador Sintáctico LR(1)")
            with st.spinner("Analizando cadena..."):
                trace_df, root = analizar_cadena_lr_con_arbol(
                    input_str, ACTION, GOTO, augmented, start
                )

            st.dataframe(trace_df, use_container_width=True)

            # Árbol de derivación
            if root is not None:
                st.subheader("🌳 Árbol de derivación")

                tab1, tab2 = st.tabs(["📊 Visualización gráfica", "📝 Representación textual"])

                with tab1:
                    if HAS_GRAPHVIZ:
                        dot = tree_to_dot(root)
                        st.graphviz_chart(dot)
                    else:
                        st.warning(
                            "⚠️ Librería `graphviz` no instalada. "
                            "Instala con: `pip install graphviz`"
                        )
                        st.code(tree_to_pretty_text(root))

                with tab2:
                    st.code(tree_to_pretty_text(root))
            else:
                st.error("❌ No se pudo construir el árbol (cadena rechazada)")

        except ValueError as e:
            st.error(f"❌ **Error en la gramática:** {str(e)}")
        except Exception as e:
            st.error(f"❌ **Error inesperado:** {str(e)}")
            with st.expander("🐛 Detalles del error"):
                st.exception(e)

# Footer
st.markdown("---")
st.caption(""" 
**Ejemplos de uso:**
- `S → CC; C → cC | d` → acepta cadenas de la forma c^i d c^j d
- `E → E+T | T; T → T*F | F; F → (E) | id` → expresiones aritméticas
""")
