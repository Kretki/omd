from pprint import pprint
from itertools import pairwise


def number_of_values(laureates_list):
    """
    Выводит количество записей в данном списке лауреатов

    Args:
        laureates_list (list): Список словарей лауреатов
    """
    print(f"Всего {len(laureates_list)} записей")


def missings_statistics(laureates_list):
    """
    Выводит статистику пропущенных значений и их долю в общем количестве

    Args:
        laureates_list (list): Список словарей лауреатов
    """
    missings = dict()
    for laureate in laureates_list:
        for key_l in laureate:
            if isinstance(laureate[key_l], list):
                for prize in laureate[key_l]:
                    for key_p in prize:
                        if prize[key_p] is None:
                            missings[key_p] = missings.get(key_p, 0) + 1
            else:
                if laureate[key_l] is None:
                    missings[key_l] = missings.get(key_l, 0) + 1
    print("Пропущенные значения:")
    pprint(missings)
    count_mis = dict()
    for laureate in laureates_list:
        for key_m in missings:
            if key_m in laureate:
                count_mis[key_m] = count_mis.get(key_m, 0) + 1
            else:
                for key_l in laureate:
                    if isinstance(laureate[key_l], list):
                        if key_m in laureate[key_l]:
                            count_mis[key_m] = count_mis.get(key_m, 0) + 1
    print("Доля пропущенных значений:")
    for key in missings:
        print(f"{key}: {missings[key]/count_mis[key]:.3f}")


def ids_analysis(laureates_list):
    """
    Выводит статистику по id, границы, наличие записей с одинаковым id
    и наличие записей с последовательными id, отличающимися более чем на 1

    Args:
        laureates_list (list): Список словарей лауреатов
    """
    number_of_values(laureates_list)
    ids_award_d = dict()
    for laureate in laureates_list:
        award_years = []
        for prizes in laureate['prizes_relevant']:
            award_years.append(prizes['award_year'])
        ids_award_d[int(laureate['id'])] = award_years
    ids_l = sorted(ids_award_d)
    print(f"Минимальный id: {ids_l[0]}, года: {ids_award_d[ids_l[0]]}")
    print(f"Максимальный id: {ids_l[-1]}, года: {ids_award_d[ids_l[-1]]}")
    ids_gaps = [(a, b, b - a) for a, b in pairwise(ids_l) if b - a > 1]
    if len(set(ids_l)) != len(ids_l):
        print("Есть записи с одинаковыми id")
    else:
        print("Нет записей с одинаковым id")
    if bool(ids_gaps):
        print("Есть записи с id отличающимися более, чем на 1")
    else:
        print("Нет записей с id отличающимися более, чем на 1")


def basic_laureates_analysis(laureates_list):
    """
    Вызывает функции технического анализа собранных данных

    Args:
        laureates_list (list): Список словарей лауреатов
    """
    number_of_values(laureates_list)
    missings_statistics(laureates_list)
    ids_analysis(laureates_list)
