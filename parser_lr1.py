# parser_lr1.py — Punto de entrada principal y API pública
"""
Parser LR(1) canónico con tablas ACTION/GOTO, FIRST/FOLLOW, traza y árbol de derivación.

Este módulo reúne todos los componentes del parser LR(1) y provee
una interfaz simple para su uso.

Ejemplo de uso:
    from parser_lr1 import (
        parse_grammar_text,
        build_parser,
        analizar_cadena_lr,
        analizar_cadena_lr_con_arbol
    )

    grammar_text = '''
    E -> E + T | T
    T -> T * F | F
    F -> ( E ) | id
    '''

    prods, start, nonterms, terms = parse_grammar_text(grammar_text)
    ACTION, GOTO, states, aug, conflicts = build_parser(prods, start, nonterms, terms)

    # Análisis simple
    result = analizar_cadena_lr("id + id * id", ACTION, GOTO, aug, start)
    print(result)

    # Análisis con árbol
    traza, arbol = analizar_cadena_lr_con_arbol("id + id", ACTION, GOTO, aug, start)
    if arbol:
        from parse_tree import tree_to_pretty_text
        print(tree_to_pretty_text(arbol))
"""

# Re-exportar funciones principales
from grammar import (
    parse_grammar_text,
    first_sets,
    first_of_seq,
    follow_sets,
    augment,
    prods_by_head,
    EPS,
    END
)

from lr1_items import (
    Item,
    closure,
    goto,
    canonical_collection
)

from parser_tables import build_tables

from parser_analyzer import (
    analizar_cadena_lr,
    analizar_cadena_lr_con_arbol
)

from parser_utils import (
    first_follow_to_df,
    action_table_df,
    goto_table_df,
    states_to_str
)

from parse_tree import (
    PTNode,
    tree_to_dot,
    tree_to_pretty_text
)


def build_parser(prods, start, nonterminals, terminals):
    """
    Función de conveniencia que construye todas las tablas del parser.

    Args:
        prods: Lista de producciones (head, body)
        start: Símbolo inicial
        nonterminals: Conjunto de no terminales
        terminals: Conjunto de terminales

    Returns:
        (ACTION, GOTO, states, aug_prods, conflicts)
    """
    FIRST = first_sets(nonterminals, terminals, prods)
    return build_tables(prods, start, terminals, nonterminals, FIRST)


__all__ = [
    # Constantes
    'EPS', 'END',
    # Gramática
    'parse_grammar_text', 'first_sets', 'first_of_seq', 'follow_sets',
    'augment', 'prods_by_head',
    # Items LR(1)
    'Item', 'closure', 'goto', 'canonical_collection',
    # Tablas
    'build_tables', 'build_parser',
    # Análisis
    'analizar_cadena_lr', 'analizar_cadena_lr_con_arbol',
    # Utilidades
    'first_follow_to_df', 'action_table_df', 'goto_table_df', 'states_to_str',
    # Árbol de derivación
    'PTNode', 'tree_to_dot', 'tree_to_pretty_text'
]