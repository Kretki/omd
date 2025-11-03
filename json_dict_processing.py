def convert_config_to_pattern(config):
    """
    Преобразует тип данных CONFIG во внутренний тип данных

    Args:
        config (dict): Паттерн конфига

    Returns:
        dict: Переделанный паттерн
    """
    result_pattern = {}
    for key, item in config.items():
        if isinstance(item, list):
            result_pattern[key] = {'path': '.'.join(item)}
        elif isinstance(item, str):
            result_pattern[key] = {'path': item}
        elif isinstance(item[0], list):
            result_pattern[key] = {'path': '.'.join(item[0]),
                                   'transform': item[1]}
        else:
            result_pattern[key] = {'path': item[0], 'transform': item[1]}
    return result_pattern


def extract_nested_value(row, pattern):
    """
    Парсит словарь согласно приведенному паттерну

    Args:
        row (dict): Словарь для парсинга
        pattern (dict): Паттерн

    Returns:
        dict: Распарсенный словарь
    """
    result_row = {}
    for key, meta in pattern.items():
        if 'path' in meta:
            meta_path: list[str] = meta['path'].split('.')
            if meta_path[0] in row:
                needed_item = row[meta_path[0]]
                for path_key in meta_path[1:]:
                    if isinstance(needed_item, list):
                        needed_item = needed_item[0]
                    elif isinstance(needed_item, dict):
                        if path_key in needed_item:
                            needed_item = needed_item[path_key]
                        else:
                            needed_item = None
                    else:
                        needed_item = None
                        break
                if 'transform' in meta:
                    if isinstance(needed_item, list):
                        new_needed_item: list[int | dict[str, str | int]] = []
                        for item in needed_item:
                            new_needed_item.append(meta['transform'](item))
                        needed_item = new_needed_item
                    else:
                        needed_item = meta['transform'](needed_item)
            else:
                needed_item = None
            result_row[key] = needed_item
    return result_row


def process_dictionary_with_config(dictionary, config):
    """
    Парсит словарь согласно приведенному конфигу

    Args:
        dictionary (dict): Словарь для парсинга
        config (dict): конфиг

    Returns:
        dict: Распарсенный словарь
    """
    pattern = convert_config_to_pattern(config)
    result_row = extract_nested_value(dictionary, pattern)
    return result_row


def process_list_of_dicts_with_config(list_of_dicts, config):
    """
    Парсит список словарей согласно конфигу

    Args:
        list_of_dicts (list): Список словарей для парсинга
        config (dict): конфиг

    Returns:
        dict: Распарсенный словарь
    """
    result_database = []
    pattern = convert_config_to_pattern(config)
    for row in list_of_dicts:
        result_row = extract_nested_value(row, pattern)
        result_database.append((result_row))
    return result_database


def create_processor(config, list_processor: bool = False):
    """
    Создает парсер по данному конфигу для list или dict в зависимости bool

    Args:
        config (dict): конфиг
        list_processor (bool): нужно парсить списки словарей или словарь

    Returns:
        Callable: парсер соответствующего запросу типа
    """
    if list_processor:
        def processor_with_list(list_of_dicts):
            return process_list_of_dicts_with_config(list_of_dicts, config)
        return processor_with_list
    else:
        def processor_with_dict(dictionary):
            return process_dictionary_with_config(dictionary, config)
        return processor_with_dict
