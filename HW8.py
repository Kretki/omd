import csv
import argparse
from pathlib import Path

def departments_hierarchy(csv_path: Path):
    """
    Выводит иерархию отделов по департаментам.

    Args:
        csv_path (Path): исходный csv файл таблицы
    """
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        result_departments : dict[str, set[str]] = dict()
        for _, row in enumerate(reader, start=2):
            if(row["Департамент"] in result_departments.keys()):
                result_departments[row["Департамент"]].add(row["Отдел"])
            else:
                result_departments[row["Департамент"]] = set([row["Отдел"]])
    for department in result_departments.keys():
        print(f"Департамент: {department}")
        for team in result_departments[department]:
            print(f"\tКоманда: {team}")

def departments_stats(csv_root_file: Path) -> dict[str, dict[str, int]]:
    """
    Считывает статстику из файла по предоставленному пути.

    Args:
        csv_root_file (Path): исходный csv файл таблицы
    
    Returns:
        dict[str, dict[str, int]]: Словарь Имя Департамента: {Размер: число, Минимальный оклад: число, Максимальный оклад: число, Суммарный оклад: число}
    """
    with csv_root_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        statistics_departments : dict[str, dict[str, int]] = dict()
        for _, row in enumerate(reader, start=2):
            if(row["Департамент"] in statistics_departments):
                statistics_departments[row["Департамент"]]["count"] += 1
                statistics_departments[row["Департамент"]]["min"] = min(statistics_departments[row["Департамент"]]["max"], int(row["Оклад"]))
                statistics_departments[row["Департамент"]]["max"] = max(statistics_departments[row["Департамент"]]["max"], int(row["Оклад"]))
                statistics_departments[row["Департамент"]]["sum"] += int(row["Оклад"])
            else:
                statistics_departments[row["Департамент"]] = {"count" : 1, "min" : int(row["Оклад"]), "max" : int(row["Оклад"]), "sum" : int(row["Оклад"])}
    return statistics_departments

def save_stats(csv_root_file: Path, csv_res_file: Path):
    """
    Принимает статистику по департаментам, вычисляет нужные параметры и сохраняет их в итоговый файл по предоставленному пути.

    Args:
        csv_root_file (Path): исходный csv файл таблицы
        csv_res_file (Path): целевой файл статистики
    """
    stats : dict[str, dict[str, int]] = departments_stats(csv_root_file)
    fieldnames = ["Департамент", "Размер", "Вилка", "Средняя зарплата"]
    with csv_res_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for department in stats.keys():
            writer.writerow({"Департамент" : department, "Размер" : str(stats[department]['count']), "Вилка" : f"{stats[department]['min']} - {stats[department]['max']}", "Средняя зарплата" : f"{stats[department]['sum'] / stats[department]['count']:.2f}"})
    print(f'Отчёт сохранён в файл: {csv_res_file}')

def main():
    """
    Основная функция выбора вариантов.
    """
    parser = argparse.ArgumentParser(
        description="csv-файлы"
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Входной csv файл",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("result_departments.csv"),
        help="Выходной файл."
    )
    args = parser.parse_args()
    print("Выберите опцию:")
    print('''
1. Вывести в понятном виде иерархию команд, т.е. департамент и все команды, которые входят в него
2. Вывести сводный отчёт по департаментам: название, численность, "вилка" зарплат в виде мин – макс, среднюю зарплату
3. Сохранить сводный отчёт из предыдущего пункта в виде csv-файла. При этом необязательно вызывать сначала команду из п.2
          ''')
    while 1:
        input_value = input()
        match input_value:
            case "1":
                departments_hierarchy(args.csv_file)
            case "2":
                statistics_departments = departments_stats(args.csv_file)
                for department in statistics_departments.keys():
                    print(f"Департамент: {department}")
                    stats = statistics_departments[department]
                    print(f"\tРазмер: {stats['count']}")
                    print(f"\tВилка: {stats['min']} - {stats['max']}")
                    print(f"\tСредняя зарплата: {stats['sum'] / stats['count']:.2f}")
            case "3":
                save_stats(args.csv_file, args.output)
            case _:
                print("Неизвестная операция. Выход из программы.")
                break


if __name__ == '__main__':
    main()