from statistics import median, mean
from itertools import product
from typing import Callable


def gb_parse_query(dict_types: dict,
                   query: str) -> tuple[list, list]:
    """
    Используется для парсинга запроса GROUP BY
    и проверки правильности запроса, существования
    столбцов в запросе и возможности исполнения
    запроса

    Args:
        dict_types(dict): Словарь ключ:тип значения
            составляющийся по всей таблице
        query(str): Запрос выданный пользователем

    Returns:
        tuple[list, list]: первый list - упорядоченный список строк
            колонок, по которым нужно группировать, второй list -
            упорядоченный список словарей колонка:функция, которые
            нужно группировать вместе с функцией, которые пользователь
            задал применить к ним.

    Raises:
        ValueError: Несоответствие запроса формату или указаны неверные
            типы передаваемых параметров.
        IndexError: Неправильно указаны столбцы, по которым происходит
            аггрегация - их количество отличается в запросе и в GROUP BY
        TypeError: Функция указанная для аггрегации для столбца со значениями
            типа str не способна аггрегировать строки
    """
    if not isinstance(dict_types, dict):
        raise ValueError("Указан неверный тип данных для парсинга запроса")
    if not isinstance(query, str):
        raise ValueError("Указан неверный тип данных для парсинга запроса")

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
        raise IndexError("Ошибка, указано недостаточно столбцов")

    for column in columns_to_function:
        for key in column:
            if column[key] != "count":
                if key in dict_types:
                    if isinstance(dict_types[key], str):
                        raise TypeError("Ошибка, невозможно аггрегировать")

    return columns_to_group, columns_to_function


def gb_str_to_fun(fun_str: str) -> Callable:
    """
    Используется для парсинга функций запроса
    пользователя, в зависимости от строки в
    запросе возвращается та или иная функция
    для аггрегации

    Args:
        fun_str(str): Входная строка названия функции

    Returns:
        Callable: функция, соответствующая названию

    Raises:
        ValueError: Указана несуществующая для обработки
            функция или указан неверный тип передаваемых значений
    """
    if not isinstance(fun_str, str):
        error = """Указан неверный тип данных для
        "формирования аггрегирующей функции"""
        raise ValueError(error)

    if fun_str == 'count':
        return len
    if fun_str == 'sum':
        return sum
    if fun_str == 'avg':
        return mean
    if fun_str == 'median':
        return median
    if fun_str == 'min':
        return min
    if fun_str == 'max':
        return max
    else:
        raise ValueError("Указана неизвестная функция для аггрегации")


def gb_build_tree(levels: list,
                  leaf_n: int) -> dict:
    """
    Строит дерево по списку списков для группировки.
    Каждому значению из уровня выше подвешивается весь
    список значений из списка следующего уровня.

    Args:
        levels(list[list]): Список списков со значениями
            столбцов, по которым происходит аггрегация
        leaf_n(int): Размер листьев, число столбцов, которые
            аггрегируются. На данном этапе создаются пустые set
            для каждого, которые далее заполнятся значениями,
            после чего к ним применятся нужные функции

    Returns:
        dict: Дерево по значениям из группировки.

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(levels, list):
        raise ValueError("Указан неверный тип данных для построения дерева")
    if not isinstance(leaf_n, int):
        raise ValueError("Указан неверный тип данных для построения дерева")

    if not levels or any(len(level) == 0 for level in levels):
        return {}

    tree: dict = {}
    for path in product(*levels):
        node = tree

        for obj in path[:-1]:
            node = node.setdefault(obj, {})

        node[path[-1]] = [set() for _ in range(leaf_n)]

    return tree


def gb_recurse_parse(tree: dict,
                     fun: Callable,
                     fun_pos: int) -> dict:
    """
    Применяет аггрегирующую функцию и укорачивает
    дерево до значений, остающихся после группировки

    Args:
        tree(dict): Дерево группировки
        fun(Callable): Аггрегирующая функция
        fun_pos(int): Позиция столбца в
            списке столбцов для аггрегирования

    Returns:
        dict: Укороченное дерево с саггрегированными значениями.

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(tree, dict):
        raise ValueError("Указан неверный тип данных для операций в дереве")
    if not isinstance(fun, Callable):
        raise ValueError("Указан неверный тип данных для операций в дереве")
    if not isinstance(fun_pos, int):
        raise ValueError("Указан неверный тип данных для операций в дереве")

    key_to_delete = []

    for key in tree:
        if isinstance(tree[key], list):
            if isinstance(tree[key][fun_pos], set):
                if len(tree[key][fun_pos]) > 0:
                    dropped_none = [val for val in tree[key][fun_pos]
                                    if val is not None]
                    tree[key][fun_pos] = fun(dropped_none)
                else:
                    tree[key][fun_pos] = None
            if all(value is None for value in tree[key]):
                key_to_delete.append(key)
        else:
            tree[key] = gb_recurse_parse(tree[key], fun, fun_pos)

    for key in key_to_delete:
        del tree[key]

    return tree


def gb_tree_to_table(tree: dict,
                     columns_to_gr: list,
                     columns_to_func: list,
                     pos: int) -> list:
    """
    Формирует из дерева таблицу обратным образом,
    превращая её в список словарей

    Args:
        data(dict): Дерево группировки
        columns_to_gr(list): Список столбцов, по которым
            производилась аггрегация
        columns_to_func(list): Список столбцов, которые
            аггрегировались
        pos(int): на каком столбце, по которому происходит
            аггрегация, мы находимся. Используется для
            рекурсивного погружения в дерево.

    Returns:
        list: Таблица, список словарей.

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(tree, dict):
        raise ValueError("Указан неверный тип данных в расформировании дерева")
    if not isinstance(columns_to_gr, list):
        raise ValueError("Указан неверный тип данных в расформировании дерева")
    if not isinstance(columns_to_func, list):
        raise ValueError("Указан неверный тип данных в расформировании дерева")
    if not isinstance(pos, int):
        raise ValueError("Указан неверный тип данных в расформировании дерева")

    subtree = []

    for key in tree:
        if isinstance(tree[key], list):
            leaf_dict = {}

            for j, col in enumerate(columns_to_func):
                leaf_dict[list(col.values())[0] +
                          "(" + list(col.keys())[0] +
                          ")"] = tree[key][j]
            subtree.append(leaf_dict)
            subtree[-1][columns_to_gr[pos]] = key
        else:
            res_d = gb_tree_to_table(tree[key],
                                     columns_to_gr,
                                     columns_to_func,
                                     pos + 1)

            for line in res_d:
                line[columns_to_gr[pos]] = key
            subtree = subtree + res_d

    return subtree


def group_by(data: list,
             sql: str) -> list:
    """
    Реализует GROUP BY, используя псевдо-SQL код.
    Сначала указываются колонки для SELECT, в нужных указывается функция
    (доступны функции COUNT, MEAN, MAX, MIN, AVG, MEDIAN)
    Функции могут применяться только к int или float, кроме функции COUNT
    Формат:
    SELECT столбец1 COUNT(столбец2) GROUP BY столбец1

    Args:
        data(dict): таблица для обработки

    Returns:
        list: обработанная group by таблица

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(data, list):
        raise ValueError("Указан неверный тип данных в GROUP BY")
    if not isinstance(sql, str):
        raise ValueError("Указан неверный тип данных в GROUP BY")

    data_types = {}

    for row in data:
        for key, val in row.items():
            data_types[key] = type(val)

    columns_to_group, columns_to_function = gb_parse_query(data_types, sql)
    result_columns = {key: set() for key in columns_to_group}

    for row in data:
        for i, column in enumerate(columns_to_group):
            if column in row:
                if row[column] is not None:
                    result_columns[column].add(row[column])

    result_columns = [list(result_columns[key]) for key in result_columns]
    tree = gb_build_tree(result_columns, len(columns_to_function))

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
        tree = gb_recurse_parse(tree, gb_str_to_fun(list(fun.values())[0]), i)

    tree = gb_tree_to_table(tree, columns_to_group, columns_to_function, 0)

    return tree


def where(data: list,
          columns: list | str,
          conditions: list | Callable) -> list:
    """
    Реализует SQL функцию WHERE. На каждый столбец из
    списка в таблице применяется функция из соответствующего
    списка функций.

    Args:
        data(list): таблица для обработки
        columns(list): список столбцов для обработки
        conditions(list): список функци, обрабатывающих столбцы

    Returns:
        list: обработанная where таблица

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
        IndexError: Если указано разное количество
            столбцов и функций
    """
    if not isinstance(data, list):
        raise ValueError("Указан неверный тип данных в WHERE")
    if not (isinstance(columns, list) or isinstance(columns, str)):
        raise ValueError("Указан неверный тип данных в WHERE")
    if not (isinstance(conditions, list) or isinstance(conditions, Callable)):
        raise ValueError("Указан неверный тип данных в WHERE")

    result_data = []

    if isinstance(columns, list):
        if len(columns) != len(conditions):
            error = "Ошибка, размеры списков столбцов и условий отличаются"
            raise IndexError(error)

        for row in data:
            row_accepted = True
            for i, column in enumerate(columns):
                if column in row:
                    if not conditions[i](row[column]):
                        row_accepted = False
                        break
            if row_accepted:
                result_data.append(row)
    else:
        for row in data:
            row_accepted = True
            if columns in row:
                if conditions(row[columns]):
                    result_data.append(row)

    return result_data


def limit(data: list,
          end: int,
          start: int = 0) -> list:
    """
    Реализует SQL функцию LIMIT.

    Args:
        data(list): таблица для обработки
        end(int): конец среза таблицы
        start(int): начало среза таблицы

    Returns:
        list: обработанная LIMIT таблица

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(data, list):
        raise ValueError("Указан неверный тип данных в LIMIT")
    if not isinstance(end, int):
        raise ValueError("Указан неверный тип данных в LIMIT")
    if not isinstance(start, int):
        raise ValueError("Указан неверный тип данных в LIMIT")

    return data[start:end]


def order_by(data: list,
             column: str,
             desc: bool = False) -> list:
    """
    Реализует SQL функцию ORDER BY.

    Args:
        data(list): таблица для обработки
        column(str): строка, по которой производить сортировку
        desc(bool): производить ли сортировку по убыванию

    Returns:
        list: обработанная ORDER BY таблица

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(data, list):
        raise ValueError("Указан неверный тип данных в ORDER BY")
    if not isinstance(column, str):
        raise ValueError("Указан неверный тип данных в ORDER BY")
    if not isinstance(desc, bool):
        raise ValueError("Указан неверный тип данных в ORDER BY")

    if not desc:
        return sorted(data, key=lambda row: row[column])

    data_s = sorted(data, key=lambda row: row[column])
    data_s.reverse()

    return data_s


def rename_column(data: list,
                  column_name: str,
                  new_column_name: str) -> list:
    """
    Переименовывает колонку таблицы.

    Args:
        data(list): таблица для обработки
        column_name(str): старое название колонки
        new_column_name(str): новое название колонки

    Returns:
        list: таблица с переименованной колонкой

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(data, list):
        raise ValueError("Указан неверный тип данных при переименовании")
    if not isinstance(column_name, str):
        raise ValueError("Указан неверный тип данных при переименовании")
    if not isinstance(new_column_name, str):
        raise ValueError("Указан неверный тип данных при переименовании")

    for row in data:
        if column_name in row:
            row[new_column_name] = row[column_name]
            del row[column_name]

    return data


def operation_column(data: list,
                     columns: list,
                     func: Callable) -> list:
    """
    Построчно применят функцию для указанных колонок.
    Значения из колонок формируются в упорядоченный список,
    по которому применяется переданная функция.

    Args:
        data(list): таблица для обработки
        columns(list): список колонок для применения функции
        func(Callable): функция для применения

    Returns:
        list: таблица с удаленными колонками и добавлением новой на месте их

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(data, list):
        raise ValueError("Указан неверный тип данных при операции")
    if not isinstance(columns, list):
        raise ValueError("Указан неверный тип данных при операции")
    if not isinstance(func, Callable):
        raise ValueError("Указан неверный тип данных при операции")

    rows_to_drop = set()

    for i, row in enumerate(data):
        value_to_aggregate = []
        missing = False
        for column in columns:
            if column in row:
                value_to_aggregate.append(row[column])
                del row[column]
            else:
                missing = True
        if missing:
            rows_to_drop.add(i)
            continue
        row["fun(" + ', '.join(columns) + ")"] = func(value_to_aggregate)

    for index in sorted(rows_to_drop, reverse=True):
        del data[index]

    return data
