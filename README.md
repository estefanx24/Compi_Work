
# LR(1) Visualizer (canónico) — estilo jsMachines

## Requisitos
```bash
pip install streamlit graphviz
```
> Para `st.graphviz_chart` no necesitas instalar binarios de Graphviz (solo la librería Python).

## Ejecutar
```bash
streamlit run app.py
```

## Uso
1. Pega la gramática (usa `ε` para vacío). No incluyas `S' -> S`; la app aumenta automáticamente.
2. Escribe la cadena con tokens separados por espacio.
3. Presiona **Construir LR(1) y simular**.

Verás:
- Producciones (human-readable)
- Tablas **ACTION/GOTO**
- Items por estado (colección canónica)
- Autómata LR(1) (transiciones por símbolo)
- Traza del análisis (shift/reduce/accept)
