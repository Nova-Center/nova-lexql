# -*- coding: utf-8 -*-

from utils.genereTreeGraphviz2 import printTreeGraph
import json
from typing import Any, Dict, List, Union

reserved = {
    "SELECT": "SELECT",
    "FROM": "FROM",
    "WHERE": "WHERE",
    "AND": "AND",
    "OR": "OR",
    "IN": "IN",
    "COUNT": "COUNT",
    "AVG": "AVG",
    "SUM": "SUM",
    "MIN": "MIN",
    "MAX": "MAX",
}

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
    "MULTIPLY",
] + list(reserved.values())

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
t_MULTIPLY = r"\*"


def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t


def t_NUMBER(t):
    r"\d+(\.\d+)?"
    t.value = float(t.value) if "." in t.value else int(t.value)
    return t


def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFIER")
    return t


def t_COMMENT(t):
    r"//.*"
    pass


t_ignore = " \t\n"


def t_error(t):
    print(f"Caractère illégal '{t.value[0]}'")
    t.lexer.skip(1)


import ply.lex as lex

lexer = lex.lex()

json_data: Dict[str, List[Dict[str, Any]]] = {}


def load_json_file(file_path: str) -> None:
    global json_data
    with open(file_path, "r") as f:
        json_data = json.load(f)


def get_value_from_path(obj: Dict[str, Any], path: Union[str, tuple]) -> Any:
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


def p_query(p):
    """query : select_query SEMI
    | count_query SEMI
    | avg_query SEMI
    | sum_query SEMI
    | min_query SEMI
    | max_query SEMI"""
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
            if "*" in fields:
                result.append(row)
            else:
                selected = {}
                for field in fields:
                    if "." in field:
                        value = get_value_from_path(row, field)
                        if value is not None:
                            selected[field] = value
                    else:
                        if field in row:
                            selected[field] = row[field]
                if selected:
                    result.append(selected)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    p[0] = result


def p_field_list(p):
    """field_list : IDENTIFIER
    | IDENTIFIER DOT IDENTIFIER
    | field_list COMMA IDENTIFIER
    | field_list COMMA IDENTIFIER DOT IDENTIFIER
    | MULTIPLY"""
    if len(p) == 2:
        if p[1] == "*":
            p[0] = ["*"]
        else:
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
            if p[2] == "IN" and isinstance(p[1], str) and p[1].startswith('"'):
                p[0] = ("condition", p[3], p[2], p[1].strip('"'))
            else:
                p[0] = ("condition", p[1], p[2], p[3])
    elif len(p) == 6:
        if p[4] == "IN" and isinstance(p[1], str) and p[1].startswith('"'):
            p[0] = ("condition", f"{p[3]}.{p[5]}", p[4], p[1].strip('"'))
        else:
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
        print(f"Moyenne de {field}: {avg}")
        p[0] = avg
    else:
        print(f"Aucune valeur numérique trouvée pour {field}")
        p[0] = None


def p_sum_query(p):
    """sum_query : SUM IDENTIFIER FROM IDENTIFIER where_clause
    | SUM IDENTIFIER FROM IDENTIFIER"""
    field = p[2]
    table = p[4]
    where = p[5] if len(p) > 5 else None

    if table not in json_data:
        print(f"Table '{table}' non trouvée")
        return

    sum = 0
    for row in json_data[table]:
        if where is None or eval_condition(row, where):
            value = get_value_from_path(row, field)
            if isinstance(value, (int, float)):
                sum += value

    print(f"Somme de {field}: {sum}")
    p[0] = sum


def p_min_query(p):
    """min_query : MIN IDENTIFIER FROM IDENTIFIER where_clause
    | MIN IDENTIFIER FROM IDENTIFIER"""
    field = p[2]
    table = p[4]
    where = p[5] if len(p) > 5 else None

    if table not in json_data:
        print(f"Table '{table}' non trouvée")
        return

    min = None
    for row in json_data[table]:
        if where is None or eval_condition(row, where):
            value = get_value_from_path(row, field)
            if value is not None:
                if min is None or value < min:
                    min = value

    if min is not None:
        print(f"Minimum de {field}: {min}")
        p[0] = min
    else:
        print(f"Aucune valeur trouvée pour {field}")
        p[0] = None


def p_max_query(p):
    """max_query : MAX IDENTIFIER FROM IDENTIFIER where_clause
    | MAX IDENTIFIER FROM IDENTIFIER"""
    field = p[2]
    table = p[4]
    where = p[5] if len(p) > 5 else None

    if table not in json_data:
        print(f"Table '{table}' non trouvée")
        return

    max = None
    for row in json_data[table]:
        if where is None or eval_condition(row, where):
            value = get_value_from_path(row, field)
            if value is not None:
                if max is None or value > max:
                    max = value

    if max is not None:
        print(f"Maximum de {field}: {max}")
        p[0] = max
    else:
        print(f"Aucune valeur trouvée pour {field}")
        p[0] = None


def eval_condition(row: Dict[str, Any], condition: tuple) -> bool:
    if condition[0] == "condition":
        field, op, value = condition[1:]

        if op == "IN":
            if isinstance(field, str) and "." in field:
                list_value = get_value_from_path(row, field)
                return value in list_value if isinstance(list_value, list) else False
            elif isinstance(value, str) and "." in value:
                list_value = get_value_from_path(row, value)
                return field in list_value if isinstance(list_value, list) else False
        else:
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

    elif condition[0] == "logical":
        op, left, right = condition[1:]
        left_result = eval_condition(row, left)
        right_result = eval_condition(row, right)
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


import ply.yacc as yacc

parser = yacc.yacc()


def execute_query(query: str) -> Any:
    try:
        result = parser.parse(query)
        return result
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête: {str(e)}")
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python lexql.py <fichier.lql> <fichier.json>")
        sys.exit(1)

    load_json_file(sys.argv[2])

    with open(sys.argv[1], "r") as f:
        queries = f.read()
        for query in queries.split(";"):
            query = query.strip()
            if query:
                execute_query(query + ";")
