import numpy as np
import pandas as pd
from pyswarms.discrete import BinaryPSO

print("Новогодний челлендж выполнили студенты группы 22ВВВ1 ")
print("Колобов И.О. Дунюшкин В.А. Лёвин А.Д.")

# Загрузка данных
kids_wish = pd.read_csv("kids_wish.csv")
ded_moroz_wish = pd.read_csv("ded_moroz_wish.csv")

# Инициализация ограничения на количество подарков каждого вида
gift_limit = 250
calculated_twin_gifts = {}
# Первый столбец - ID подарка, остальные - ID детей по приоритету
gift_ids = ded_moroz_wish.iloc[:, 0]

# Создание структуры данных для приоритетов Деда Мороза с учетом ограничений
ded_moroz_priorities = {}
for gift_id, row in zip(gift_ids, ded_moroz_wish.itertuples(index=False, name=None)):
    deserving_list = list(row[1:])

    # Убедимся, что количество подарков не превышает лимит
    if len(deserving_list) > gift_limit:
        deserving_list = deserving_list[:gift_limit]

    ded_moroz_priorities[int(gift_id)] = deserving_list

# Создание структур данных для приоритетов детей и Деда Мороза
kids_priorities = {int(str(row.iloc[0])[0]): row.iloc[1:].tolist() for _, row in kids_wish.iterrows()}
twins_mapping = {i: kids_wish.iloc[i, 0] for i in range(len(kids_wish))}

# Добавьте глобальные переменные для хранения вычисленных очков
calculated_kids_scores = {}
calculated_dedmoroz_scores = {}

def calculate_happiness_index_kids(child_id, gift_id):
    # Проверьте, были ли уже вычислены подарки для этого близнеца
    if child_id in twins_mapping:
        twin_id = twins_mapping[child_id]
        if (twin_id, gift_id) in calculated_twin_gifts:
            return calculated_twin_gifts[(twin_id, gift_id)]

    if child_id not in kids_priorities:
        return -1  # В случае ошибки, например, если child_id не найден

    # Получаем список приоритетов ребенка
    wish_list = kids_priorities[child_id]

    # Определяем индекс подарка в списке желаемых подарков ребенка
    try:
        gift_index = wish_list.index(gift_id)
    except ValueError:
        return -1  # В случае, если подарок не найден в списке желаемых

    # Вычисляем СчастьеРебенка
    happiness_child = 2 * (100 - gift_index)

    # Обработка для близнецов
    if child_id in twins_mapping:
        twin_id = twins_mapping[child_id]
        # Сохраняем вычисленные подарки для близнецов
        calculated_twin_gifts[(child_id, gift_id)] = happiness_child
        calculated_twin_gifts[(twin_id, gift_id)] = happiness_child

    # Сохраняем вычисленные очки в словаре
    calculated_kids_scores[(child_id, gift_id)] = happiness_child

    return happiness_child

def calculate_happiness_index_ded_moroz(gift_id, child_id):
    # Проверьте, были ли уже вычислены очки для этой пары
    if (gift_id, child_id) in calculated_dedmoroz_scores:
        return calculated_dedmoroz_scores[(gift_id, child_id)]

    if gift_id not in ded_moroz_priorities:
        return -1  # В случае ошибки, например, если gift_id не найден

    # Получаем список приоритетов Деда Мороза для подарка
    deserving_list = ded_moroz_priorities[gift_id]

    # Определяем индекс ребенка в списке заслуживающих подарок
    try:
        child_index = deserving_list.index(child_id)
    except ValueError:
        return -1  # В случае, если ребенок не найден в списке заслуживающих

    # Вычисляем СчастьеДедаМороза
    happiness_ded_moroz = 2 * (100 - child_index)

    # Сохраняем вычисленные очки в словаре
    calculated_dedmoroz_scores[(gift_id, child_id)] = happiness_ded_moroz

    return happiness_ded_moroz

def calculate_happiness_index(solution):
    child_ids = np.where(solution == 1)[0]
    num_children = len(kids_wish)
    total_happiness = 0
    for child_id in child_ids:
        for gift_id in range(num_gifts):
            happiness_child = calculate_happiness_index_kids(child_id, gift_id)
            total_happiness += happiness_child

            happiness_dedmoroz = calculate_happiness_index_ded_moroz(gift_id, child_id)
            total_happiness += happiness_dedmoroz

    return total_happiness

# Количество детей и подарков
num_children = len(kids_wish)
num_gifts = len(gift_ids.unique())  # Используйте unique() для получения уникальных значений

# Создание роя частиц
options = {'c1': 0.5, 'c2': 0.3, 'w': 0.5, 'k': 10, 'p': 2}
optimizer = BinaryPSO(n_particles=20, dimensions=num_children, options=options)
# Оптимизация
cost, best_solution = optimizer.optimize(calculate_happiness_index, iters=20)

# Получение индексов выбранных детей
selected_children_indices = np.where(best_solution == 1)[0]
# Получение индексов соответствующих подарков
selected_gifts_indices = np.arange(num_gifts)[selected_children_indices]
# Создание DataFrame с результатами
result_df = pd.DataFrame({"ChildId": selected_children_indices, "GiftId": selected_gifts_indices})
# Сохранение результата в CSV файл
result_df.to_csv("solution.csv", index=False)
