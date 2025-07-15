# -*- coding: utf-8 -*-

from genereTreeGraphviz2 import printTreeGraph
import json
import re
from typing import Any, Dict, List, Union

# Mots réservés du langage
reserved = {
    "SELECT": "SELECT",
    "FROM": "FROM",
    "WHERE": "WHERE",
    "AND": "AND",
    "OR": "OR",
    "IN": "IN",
    "COUNT": "COUNT",
    "AVG": "AVG",
}

# Définition des tokens
tokens = [
    "NUMBER",
    "STRING",
    "IDENTIFIER",
    "DOT",
    "COMMA",
    "SEMI",
    "EQUALS",
    "GT",
    "LT",
    "GTE",
    "LTE",
    "NOTEQUALS",
    "LPAREN",
    "RPAREN",
    "LBRACKET",
    "RBRACKET",
] + list(reserved.values())

# Règles des tokens simples
t_DOT = r"\."
t_COMMA = r","
t_SEMI = r";"
t_EQUALS = r"=="
t_GT = r">"
t_LT = r"<"
t_GTE = r">="
t_LTE = r"<="
t_NOTEQUALS = r"!="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"


def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Enlève les guillemets
    return t


def t_NUMBER(t):
    r"\d+(\.\d+)?"
    t.value = float(t.value) if "." in t.value else int(t.value)
    return t


def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFIER")
    return t


# Ignorer les espaces et les commentaires
def t_COMMENT(t):
    r"//.*"
    pass


t_ignore = " \t\n"


def t_error(t):
    print(f"Caractère illégal '{t.value[0]}'")
    t.lexer.skip(1)


# Construction du lexer
import ply.lex as lex

lexer = lex.lex()

# Variables globales pour stocker les données
json_data: Dict[str, List[Dict[str, Any]]] = {}


def load_json_file(file_path: str) -> None:
    """Charge un fichier JSON dans la mémoire."""
    global json_data
    with open(file_path, "r") as f:
        json_data = json.load(f)


def get_value_from_path(obj: Dict[str, Any], path: Union[str, tuple]) -> Any:
    """Récupère une valeur à partir d'un chemin JSON (e.g., 'details.skills')."""
    if isinstance(path, tuple):
        path = ".".join(path)
    parts = path.split(".")
    current = obj
    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        else:
            return None
    return current


# Règles de grammaire
def p_query(p):
    """query : select_query SEMI
    | count_query SEMI
    | avg_query SEMI"""
    p[0] = p[1]


def p_select_query(p):
    """select_query : SELECT field_list FROM IDENTIFIER where_clause
    | SELECT field_list FROM IDENTIFIER"""
    table = p[4]
    fields = p[2]
    where = p[5] if len(p) > 5 else None

    if table not in json_data:
        print(f"Table '{table}' non trouvée")
        return

    result = []
    for row in json_data[table]:
        if where is None or eval_condition(row, where):
            selected = {}
            for field in fields:
                # Si le champ contient un point, c'est un chemin JSON
                if "." in field:
                    value = get_value_from_path(row, field)
                    if value is not None:
                        selected[field] = value
                else:
                    if field in row:
                        selected[field] = row[field]
            if selected:  # N'ajouter que si des champs ont été sélectionnés
                result.append(selected)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    p[0] = result


def p_field_list(p):
    """field_list : IDENTIFIER
    | IDENTIFIER DOT IDENTIFIER
    | field_list COMMA IDENTIFIER
    | field_list COMMA IDENTIFIER DOT IDENTIFIER"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        if p[2] == ".":
            p[0] = [f"{p[1]}.{p[3]}"]
        else:
            p[0] = p[1] + [p[3]]
    else:
        p[0] = p[1] + [f"{p[3]}.{p[5]}"]


def p_where_clause(p):
    """where_clause : WHERE condition"""
    p[0] = p[2]


def p_condition(p):
    """condition : IDENTIFIER operator expression
    | IDENTIFIER DOT IDENTIFIER operator expression
    | STRING operator expression
    | condition AND condition
    | condition OR condition
    | LPAREN condition RPAREN"""
    if len(p) == 4:
        if p[1] == "(":
            p[0] = p[2]
        elif p[2] in ["AND", "OR"]:
            p[0] = ("logical", p[2], p[1], p[3])
        else:
            p[0] = ("condition", p[1], p[2], p[3])
    elif len(p) == 6:
        p[0] = ("condition", f"{p[1]}.{p[3]}", p[4], p[5])


def p_operator(p):
    """operator : EQUALS
    | GT
    | LT
    | GTE
    | LTE
    | NOTEQUALS
    | IN"""
    p[0] = p[1]


def p_expression(p):
    """expression : NUMBER
    | STRING
    | IDENTIFIER
    | IDENTIFIER DOT IDENTIFIER
    | LBRACKET value_list RBRACKET"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        if p[2] == ".":
            p[0] = f"{p[1]}.{p[3]}"
        else:
            p[0] = p[2]
    else:
        p[0] = p[2]


def p_value_list(p):
    """value_list : expression
    | value_list COMMA expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_count_query(p):
    """count_query : COUNT FROM IDENTIFIER where_clause
    | COUNT FROM IDENTIFIER"""
    table = p[3]
    where = p[4] if len(p) > 4 else None

    if table not in json_data:
        print(f"Table '{table}' non trouvée")
        return

    count = 0
    for row in json_data[table]:
        if where is None or eval_condition(row, where):
            count += 1

    print(f"Count: {count}")
    p[0] = count


def p_avg_query(p):
    """avg_query : AVG IDENTIFIER FROM IDENTIFIER where_clause
    | AVG IDENTIFIER FROM IDENTIFIER"""
    field = p[2]
    table = p[4]
    where = p[5] if len(p) > 5 else None

    if table not in json_data:
        print(f"Table '{table}' non trouvée")
        return

    values = []
    for row in json_data[table]:
        if where is None or eval_condition(row, where):
            value = get_value_from_path(row, field)
            if isinstance(value, (int, float)):
                values.append(value)

    if values:
        avg = sum(values) / len(values)
        print(f"Average of {field}: {avg}")
        p[0] = avg
    else:
        print(f"No numeric values found for {field}")
        p[0] = None


def eval_condition(row: Dict[str, Any], condition: tuple) -> bool:
    """Évalue une condition sur une ligne de données."""
    if condition[0] == "condition":
        field, op, value = condition[1:]
        # Si field est un tuple ou une chaîne avec un point, utiliser get_value_from_path
        if isinstance(field, tuple) or (isinstance(field, str) and "." in field):
            row_value = get_value_from_path(row, field)
        else:
            row_value = row.get(field)

        if row_value is None:
            return False

        if op == "==":
            return row_value == value
        elif op == ">":
            return row_value > value
        elif op == "<":
            return row_value < value
        elif op == ">=":
            return row_value >= value
        elif op == "<=":
            return row_value <= value
        elif op == "!=":
            return row_value != value
        elif op == "IN":
            if isinstance(row_value, list):
                return value in row_value
            elif isinstance(value, list):
                return row_value in value
            return False

    elif condition[0] == "logical":
        op, left, right = condition[1:]
        print(f"Logical operator: {op}")
        print(f"Left condition: {left}")
        print(f"Right condition: {right}")
        left_result = eval_condition(row, left)
        print(f"Left result: {left_result}")
        if op == "AND" and not left_result:  # Short-circuit AND
            return False
        right_result = eval_condition(row, right)
        print(f"Right result: {right_result}")
        if op == "AND":
            return left_result and right_result
        elif op == "OR":
            return left_result or right_result

    return False


def p_error(p):
    if p:
        print(f"Erreur de syntaxe à '{p.value}'")
    else:
        print("Erreur de syntaxe à la fin de l'entrée")


# Construction du parser
import ply.yacc as yacc

parser = yacc.yacc()


def execute_query(query: str) -> Any:
    """Exécute une requête LexQL."""
    try:
        result = parser.parse(query)
        return result
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête: {str(e)}")
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python lexql.py <fichier.lql>")
        sys.exit(1)

    # Charge le fichier JSON de données
    load_json_file("data.json")

    # Lit et exécute le fichier .lql
    with open(sys.argv[1], "r") as f:
        queries = f.read()
        for query in queries.split(";"):
            query = query.strip()
            if query:
                execute_query(query + ";")
