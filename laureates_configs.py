from prizes_configs import prize_processor
from json_dict_processing import create_processor
from typing import Callable


def process_year(year_string: str) -> int:
    """
    Функция вытаскивает год из поля DATE

    Args:
        year_string (str): дата

    Returns:
        int: год в виде числа

    Raises:
        ValueError: Если указаны неверные типы
            передаваемого параметра.
    """
    if not isinstance(year_string, str):
        raise ValueError("Указан неверный тип данных при обработке")
    return int(year_string.split('-')[0])


CONFIG_PERSON = {
    'id': 'id',
    'name': ['knownName', 'en'],
    'gender': 'gender',
    'birth_year': (['birth', 'date'], process_year),
    'country_birth': ['birth', 'place', 'country', 'en'],
    'country_now': ['birth', 'place', 'countryNow', 'en'],
    'prizes_relevant': ('nobelPrizes', prize_processor())
}


CONFIG_ORG = {
    'id': 'id',
    'name': ['orgName', 'en'],
    'founded_year': (['founded', 'date'], process_year),
    'country_founded': ['founded', 'place', 'country', 'en'],
    'country_now': ['founded', 'place', 'countryNow', 'en'],
    'prizes_relevant': ('nobelPrizes', prize_processor())
}


def person_processor() -> Callable:
    """
    Функция создает парсер по CONFIG_PERSON

    Returns:
        Callable: парсер для людей
    """
    return create_processor(CONFIG_PERSON)


def org_processor() -> Callable:
    """
    Функция создает парсер по CONFIG_ORG

    Returns:
        Callable: парсер для организаций
    """
    return create_processor(CONFIG_ORG)
