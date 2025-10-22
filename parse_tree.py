from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PTNode:
    label: str
    children: List["PTNode"]
    id: Optional[int] = None

def _next_id():
    _next_id.counter += 1
    return _next_id.counter

_next_id.counter = 0

def tree_to_dot(root: PTNode) -> str:
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
    s = indent + root.label + "\n"
    for ch in root.children:
        s += tree_to_pretty_text(ch, indent + "  ")
    return s
