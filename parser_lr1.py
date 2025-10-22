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
    FIRST = first_sets(nonterminals, terminals, prods)
    return build_tables(prods, start, terminals, nonterminals, FIRST)

__all__ = [
    'EPS', 'END',
    'parse_grammar_text', 'first_sets', 'first_of_seq', 'follow_sets',
    'augment', 'prods_by_head',
    'Item', 'closure', 'goto', 'canonical_collection',
    'build_tables', 'build_parser',
    'analizar_cadena_lr', 'analizar_cadena_lr_con_arbol',
    'first_follow_to_df', 'action_table_df', 'goto_table_df', 'states_to_str',
    'PTNode', 'tree_to_dot', 'tree_to_pretty_text'
]
