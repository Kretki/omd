from typing import Any, Callable


def find_value_extracting(row: dict,
                          path_list: list) -> Any:
    """
    Используется для последовательного перехода по
    словарю согласно последовательности ключей
    в списке.

    Args:
        row (dict): Словарь для парсинга
        path_list(list[str]): Последовательность путей

    Returns:
        Any: значение, которое лежало по концу пути, или None,
             если путя не существует.

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(row, dict):
        raise ValueError("Указан неверный тип данных для парсинга словаря")
    if not isinstance(path_list, list):
        raise ValueError("Указан неверный тип данных для парсинга словаря")

    sub_row = row
    for path_el in path_list:
        if path_el not in sub_row:
            return None
        else:
            sub_row = sub_row[path_el]

    return sub_row


def extract_value_config(row: dict,
                         config: dict) -> dict:
    """
    Создает новый словарь из данного
    согласно конфигу заданного формата.

    Args:
        row (dict): Словарь для парсинга
        path_list(list[str]): Последовательность путей

    Returns:
        dict: Словарь, соответствующий формату в конфиге

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(row, dict):
        raise ValueError("Указан неверный тип данных для парсинга словаря")
    if not isinstance(config, dict):
        raise ValueError("Указан неверный тип данных для парсинга словаря")
    result_dict = {}

    for key in config:
        if isinstance(config[key], tuple):
            if isinstance(config[key][0], list):
                ret_value = find_value_extracting(row, config[key][0])
                if ret_value is None:
                    result_dict[key] = None
                else:
                    result_dict[key] = config[key][1](ret_value)
            else:
                if isinstance(row[config[key][0]], list):
                    result_dict[key] = []
                    for li_el in row[config[key][0]]:
                        result_dict[key].append(config[key][1](li_el))
                else:
                    result_dict[key] = config[key][1](row[config[key][0]])
        elif isinstance(config[key], list):
            result_dict[key] = find_value_extracting(row, config[key])
        else:
            result_dict[key] = row[config[key]]

    return result_dict


def process_dictionary_with_config(dictionary: dict,
                                   config: dict) -> dict:
    """
    Парсит словарь согласно приведенному конфигу

    Args:
        dictionary (dict): Словарь для парсинга
        config (dict): конфиг

    Returns:
        dict: Распарсенный словарь

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(dictionary, dict):
        raise ValueError("Указан неверный тип данных для парсинга словаря")
    if not isinstance(config, dict):
        raise ValueError("Указан неверный тип данных для парсинга словаря")

    result_row = extract_value_config(dictionary, config)

    return result_row


def process_list_of_dicts_with_config(list_of_dicts: list,
                                      config: dict) -> list:
    """
    Парсит список словарей согласно конфигу

    Args:
        list_of_dicts (list): Список словарей для парсинга
        config (dict): конфиг

    Returns:
        list: Список словарей, таблица из словарей нового формата

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(list_of_dicts, list):
        raise ValueError("Указан неверный тип данных для парсинга словаря")
    if not isinstance(config, dict):
        raise ValueError("Указан неверный тип данных для парсинга словаря")

    result_database = []

    for row in list_of_dicts:
        result_row = extract_value_config(row, config)
        result_database.append((result_row))

    return result_database


def create_processor(config: dict,
                     list_processor: bool = False) -> Callable:
    """
    Создает парсер по данному конфигу для list или dict в зависимости bool

    Args:
        config (dict): конфиг
        list_processor (bool): нужно парсить списки словарей или словарь

    Returns:
        Callable: парсер соответствующего запросу типа

    Raises:
        ValueError: Если указаны неверные типы
            передаваемых параметров.
    """
    if not isinstance(list_processor, bool):
        raise ValueError("Указан неверный тип данных для создания процессора")
    if not isinstance(config, dict):
        raise ValueError("Указан неверный тип данных для создания процессора")

    if list_processor:
        def processor_with_list(list_of_dicts):
            return process_list_of_dicts_with_config(list_of_dicts, config)
        return processor_with_list

    else:
        def processor_with_dict(dictionary):
            return process_dictionary_with_config(dictionary, config)
        return processor_with_dict
