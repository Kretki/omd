from statistics import median, mean
from itertools import product


def group_by_parse_query(row, query):
    query = query.replace("\n", " ")
    query = query.lower()
    query = query.split(" ")
    if query[0] != "select":
        raise ValueError("Ошибка, первым должен идти SELECT в GROUP BY")
    if "group" not in query:
        raise ValueError("Ошибка, не указан GROUP BY в группировке")
    if query[query.index("group") + 1] != "by":
        raise ValueError("Ошибка, неправильно указан GROUP BY")
    columns_to_group = []
    columns_to_check = set()
    columns_to_function = []
    for column in query[1:query.index("group")]:
        if "(" not in column:
            columns_to_check.add(column)
        else:
            func, column = column.split("(")
            column = column[:len(column) - 1]
            columns_to_function.append({column: func})
    for column in query[query.index("group") + 2:]:
        columns_to_group.append(column)
    if set(columns_to_group) != columns_to_check:
        raise ValueError("Ошибка, указано недостаточно столбцов")
    for column in columns_to_function:
        for key in column:
            if column[key] != "count":
                if key in row:
                    if isinstance(row[key], str):
                        raise ValueError("Ошибка, невозможно аггрегировать")
    return columns_to_group, columns_to_function


def str_to_fun(fun_str):
    if fun_str == 'count':
        return len
    if fun_str == 'sum':
        return sum
    if fun_str == 'mean':
        return mean
    if fun_str == 'median':
        return median
    if fun_str == 'min':
        return min
    if fun_str == 'max':
        return max


def build_tree(levels, leaf_n):
    """
    Строит дерево по списку списков для группировки
    """
    if not levels or any(len(level) == 0 for level in levels):
        return {}

    tree: dict = {}
    for path in product(*levels):
        node = tree
        for obj in path[:-1]:
            node = node.setdefault(obj, {})
        node[path[-1]] = leaf_n * [set()]
    return tree


def recurse_parse(tree, fun, fun_pos):
    key_to_delete = []
    for key in tree:
        if isinstance(tree[key], list):
            if isinstance(tree[key][fun_pos], set):
                if len(tree[key][fun_pos]) > 0:
                    tree[key][fun_pos] = fun(tree[key][fun_pos])
                else:
                    del tree[key][fun_pos]
            if len(tree[key]) == 0:
                key_to_delete.append(key)
        else:
            tree[key] = recurse_parse(tree[key], fun, fun_pos)
    for key in key_to_delete:
        del tree[key]
    return tree


def dict_to_table(data, columns_to_gr, columns_to_func, i):
    res = []
    for key in data:
        if isinstance(data[key], list):
            for j, col in enumerate(columns_to_func):
                res.append({list(col.keys())[0]: data[key][j]})
                res[-1][columns_to_gr[i]] = key
        else:
            res_d = dict_to_table(data[key], columns_to_gr, columns_to_func, i + 1)
            for line in res_d:
                line[columns_to_gr[i]] = key
            res = res + res_d
    return res


def group_by(data, sql):
    """
    Функция использует псевдо-SQL код. Сначала указываются колонки для
    SELECT, в нужных указывается функция (доступны функции COUNT, MEAN,
    MAX, MIN, MEDIAN) Функции могут применяться только к int или float,
    кроме функции COUNT. Остальные должны находиться в GROUP BY ниже
    Формат:
    SELECT столбец1 COUNT(столбец2) GROUP BY столбец1

    Args:
        data(dict): таблица для обработки

    Returns:
        dict: обработанная group by таблица
    """
    columns_to_group, columns_to_function = group_by_parse_query(data[0], sql)

    result_columns = {key: set() for key in columns_to_group}
    for row in data:
        for i, column in enumerate(columns_to_group):
            if column in row:
                if row[column] is not None:
                    result_columns[column].add(row[column])
    result_columns = [list(result_columns[key]) for key in result_columns]
    tree = build_tree(result_columns, len(columns_to_function))
    for row in data:
        skip_row = False
        row_path = []
        for column in columns_to_group:
            if column in row and row[column] is not None:
                row_path.append(row[column])
            else:
                skip_row = True
        if skip_row:
            continue
        for i, column in enumerate(columns_to_function):
            key = list(column.keys())[0]
            if key in row:
                tree_pointer = tree
                for path in row_path:
                    tree_pointer = tree_pointer[path]
                tree_pointer[i].add(row[key])
    for i, fun in enumerate(columns_to_function):
        tree = recurse_parse(tree, str_to_fun(list(fun.values())[0]), i)
    tree = dict_to_table(tree, columns_to_group, columns_to_function, 0)
    return tree


def where(data, condition_fun):
    result_data = []
    for row in data:
        if condition_fun(row):
            result_data.append(row)
    return result_data


def limit(data, value):
    return data[:value]


def order_by(data, column, desc=False):
    if not desc:
        return sorted(data, key=lambda row: row[column])
    data_s = sorted(data, key=lambda row: row[column])
    data_s.reverse()
    return data_s
