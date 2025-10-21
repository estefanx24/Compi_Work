#new
import streamlit as st
from parser import build_parser
from visitor import Interpreter

st.set_page_config(page_title="LR(1) Parser (sin conflictos con stdlib)", layout="wide")
st.title("LR(1) Parser en Python — versión sin conflictos de nombres")

code = st.text_area("Código", value=(
"x=9;\n"
"y=2+3*4;\n"
"print(sqrt(x)+y);\n"
"if x then print(1) else print(0) endif;\n"
"while y do y=y-5 endwhile;\n"
"print(y)\n"
), height=220)

col1, col2 = st.columns(2)
parser, states, ACTION, GOTO = build_parser()

with col1:
    if st.button("Parsear y ejecutar"):
        try:
            ast = parser.parse(code)
            out = Interpreter().run(ast)
            st.success("Parseo exitoso.")
            st.subheader("Salida")
            st.code(out or "(sin salida)")
        except Exception as e:
            st.error(str(e))

with col2:
    st.subheader("Estados LR(1)")
    st.write(f"Total: **{len(states)}**")
    preview = []
    for i, I in enumerate(states[:10]):
        preview.append(f"I{i}: " + ", ".join([f"[{p.prod_idx}:{p.dot}, {p.look}]" for p in list(I)[:6]]) + (" ..." if len(I)>6 else ""))
    st.code("\n".join(preview))

st.markdown("---")
with st.expander("ACTION / GOTO (parcial)"):
    st.text("ACTION:"); st.code("\n".join([f"{k}: {v}" for k,v in list(ACTION.items())[:80]]) + ("\n..." if len(ACTION)>80 else ""))
    st.text("GOTO:");   st.code("\n".join([f"{k}: {v}" for k,v in list(GOTO.items())[:80]]) + ("\n..." if len(GOTO)>80 else ""))
