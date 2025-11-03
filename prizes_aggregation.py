from statistics import median, mean


def prizes_aggregation(laureates_list):
    """
    Так как может быть несколько премий у лауреатов в разные года
    то их нужно саггрегировать в одни данные (чтобы не реализовывать JOIN)
    Функция убирает prizes_relevant у каждого лауреата и добавляет
    максимальное, минимальное, среднее, медаинное значения для численных
    параметров для лауреатов со статусом received (остальных придется
    откинуть, так как без JOIN неясно что с ними делать). В случае,
    если категорий по которым была получена награда несколько, то
    остается первая для всех

    Args:
        laureates_list (list): список словарей по лауреатам в заданном
        конфигами формате

    Returns:
        list: список словарей, value у которых только str, int или float
    """

    for laureate in laureates_list:
        if 'prizes_relevant' not in laureate:
            continue
        if len(laureate['prizes_relevant']) == 1:
            for key in laureate['prizes_relevant'][0]:
                laureate[key] = laureate['prizes_relevant'][0][key]
            del laureate['prizes_relevant']
        else:
            new_d = dict()
            for prize in laureate['prizes_relevant']:
                if prize['prize_status'] != 'received':
                    break
                for key in prize:
                    new_d[key] = new_d.get(key, []) + [prize[key]]
            minimum_year = min(enumerate(new_d['award_year']),
                               key=lambda x: x[1])[0]
            new_d['category_en'] = new_d['category_en'][minimum_year]
            del laureate['prizes_relevant']
            laureate['count_prizes'] = len(new_d['prize_amount'])
            for key in ['prize_amount', 'prize_amount_adjusted', 'award_year']:
                laureate[key+'_min'] = min(new_d[key])
                laureate[key+'_max'] = max(new_d[key])
                laureate[key+'_median'] = median(new_d[key])
                laureate[key+'_mean'] = mean(new_d[key])
            for key in ['prize_amount', 'prize_amount_adjusted']:
                laureate[key+'_sum'] = sum(new_d[key])
            laureate['category_en'] = new_d['category_en']
    return laureates_list
