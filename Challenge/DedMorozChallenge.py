import numpy as np
import pandas as pd
#from scipy.optimize import minimize
from pyswarms.discrete import BinaryPSO

print(f"Новогодний челлендж выполнили студенты группы 22ВВВ1 ")
print(f"Колобов И.О. Дунюшкин В.А. Лёвин А.Д.")

# Загрузка данных
kids_wish = pd.read_csv("kids_wish.csv")
ded_moroz_wish = pd.read_csv("ded_moroz_wish.csv")

# Создание структур данных для приоритетов детей и Деда Мороза
kids_priorities = {}
ded_moroz_priorities = {}

child_id_column_index = 0
gift_id_column_index = 0

# Заполнение структуры данных для приоритетов детей
for index, row in kids_wish.iterrows():
    child_id = int(str(row.iloc[0])[0])  # Используем первую цифру в качестве идентификатора ребенка
    wish_list = row.iloc[1:].tolist()
    kids_priorities[child_id] = wish_list

# Заполнение структуры данных для приоритетов Деда Мороза
for index, row in ded_moroz_wish.iterrows():
    gift_id = int(str(row.iloc[0])[0])  # Используем первую цифру в качестве идентификатора подарка
    deserving_list = row.iloc[1:].tolist()
    ded_moroz_priorities[gift_id] = deserving_list

twins_mapping = {i: kids_wish.iloc[i, 0] for i in range(len(kids_wish))}

def calculate_happiness_index_kids(child_id, gift_id, kids_priorities, twins_mapping):
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

    # Используем twins_mapping, если необходимо
    twin_id = twins_mapping.get(child_id, None)
    if twin_id is not None:
        # Обрабатываем логику, специфичную для близнецов, если необходимо
        pass

    return happiness_child

def calculate_happiness_index_ded_moroz(gift_id, child_id, ded_moroz_priorities):
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

    return happiness_ded_moroz


def calculate_happiness_index(solution):
    child_ids = np.where(solution == 1)[0]
    gift_ids = np.arange(num_gifts)

    total_happiness = 0
    for child_id, gift_id in zip(child_ids, gift_ids[child_ids]):
        happiness_child = calculate_happiness_index_kids(child_id, gift_id, kids_priorities, twins_mapping)
        total_happiness += happiness_child

        happiness_dedmoroz = calculate_happiness_index_ded_moroz(gift_id, child_id, ded_moroz_priorities)
        total_happiness += happiness_dedmoroz

    return total_happiness

# Количество детей и подарков
num_children = len(kids_wish)
num_gifts = len(ded_moroz_wish)

# Создание роя частиц
options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9, 'k': 30, 'p': 2}
optimizer = BinaryPSO(n_particles=100, dimensions=num_children, options=options)

# Оптимизация
cost, best_solution = optimizer.optimize(calculate_happiness_index, iters=100)


# Получение индексов выбранных детей
selected_children_indices = np.where(best_solution == 1)[0]
# Получение индексов соответствующих подарков
selected_gifts_indices = np.arange(num_gifts)[selected_children_indices]
# Создание DataFrame с результатами
result_df = pd.DataFrame({"ChildId": selected_children_indices, "GiftId": selected_gifts_indices})
# Сохранение результата в CSV файл
result_df.to_csv("optimized_solution.csv", index=False)