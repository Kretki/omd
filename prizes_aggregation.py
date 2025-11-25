def prizes_aggregation(laureates_list: list) -> list:
    """
    Функция вычленяет призы из участников и делает из словаря,
    в котором есть список словарей с дублирующими
    значениями участников.

    Args:
        laureates_list (list): список словарей по лауреатам в заданном
        конфигами формате

    Returns:
        list: список словарей, value у которых только str, int или float

    Raises:
        ValueError: При неверном типе входных данных.
    """
    if not isinstance(laureates_list, list):
        raise ValueError("Указан неверный тип данных для обработки призов")

    additional_list = []

    for laureate in laureates_list:
        if 'prizes_relevant' not in laureate:
            continue

        if len(laureate['prizes_relevant']) == 1:

            for key in laureate['prizes_relevant'][0]:
                laureate[key] = laureate['prizes_relevant'][0][key]

            del laureate['prizes_relevant']

            laureate['prize_no'] = 1

        else:
            for key in laureate['prizes_relevant'][0]:
                laureate[key] = laureate['prizes_relevant'][0][key]
                laureate['prize_no'] = 1

            for num_prize, prize in enumerate(laureate['prizes_relevant'][1:]):
                new_laureate = laureate.copy()

                del new_laureate['prizes_relevant']

                for key in prize:
                    laureate[key] = prize[key]

                new_laureate['prize_no'] = num_prize + 2
                additional_list.append(new_laureate)

            del laureate['prizes_relevant']

    laureates_list += additional_list

    return laureates_list
