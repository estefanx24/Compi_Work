# parse_tree.py — Árbol de derivación (parse tree)
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PTNode:
    """Nodo del árbol de derivación."""
    label: str
    children: List["PTNode"]
    id: Optional[int] = None  # para DOT


def _next_id():
    """Generador de IDs únicos para nodos."""
    _next_id.counter += 1
    return _next_id.counter


_next_id.counter = 0


def tree_to_dot(root: PTNode) -> str:
    """
    Exporta el árbol en formato DOT (Graphviz).

    Args:
        root: Nodo raíz del árbol

    Returns:
        String con la representación DOT del árbol
    """
    lines = ["digraph G {", 'node [shape=ellipse];']

    def walk(n: PTNode):
        if n.id is None:
            n.id = _next_id()
        lines.append(f'  n{n.id} [label="{n.label}"];')
        for ch in n.children:
            if ch.id is None:
                ch.id = _next_id()
            lines.append(f'  n{n.id} -> n{ch.id};')
            walk(ch)

    walk(root)
    lines.append("}")
    return "\n".join(lines)


def tree_to_pretty_text(root: PTNode, indent: str = "") -> str:
    """
    Convierte el árbol a texto con indentación.

    Args:
        root: Nodo raíz del árbol
        indent: String de indentación actual

    Returns:
        Representación en texto del árbol
    """
    s = indent + root.label + "\n"
    for ch in root.children:
        s += tree_to_pretty_text(ch, indent + "  ")
    return s