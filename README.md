
# Parser LR(1) — versión sin conflictos con la librería estándar

**Problema original**: archivos llamados `token.py` y `ast.py` chocan con los módulos
estándar `token` y `ast` que usa Python internamente → provoca errores al importar `dataclasses`.

**Solución**: renombramos a `tok.py` y `ast_nodes.py` y actualizamos imports.

### Archivos
- `tok.py` — tipos de token y `Token`.
- `scanner.py` — lexer `lex(code)`.
- `parser.py` — generador LR(1) (closure/goto), tablas ACTION/GOTO, runtime LR, gramática y semántica.
- `ast_nodes.py` — nodos del AST.
- `visitor.py` — intérprete del AST.
- `main_cli.py` — prueba por consola.
- `app.py` — interfaz con Streamlit.

### Ejecutar
```bash
python main_cli.py
# o
pip install streamlit
streamlit run app.py
```
