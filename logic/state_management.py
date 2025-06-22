# logic/state_management.py

skill_to_tactic = {
    "STR": {"name": "Сокрушительный Натиск", "type": "single"},
    "INT": {"name": "Когнитивный Ураган", "type": "single"},
    "END": {"name": "Неугасимый Феникс", "type": "single"},
    "TEC": {"name": "Плазменный Импульс", "type": "single"},
    "DEF": {"name": "Незыблемый Бастион", "type": "single"},
    "STR,INT": {"name": "Тактический Кулак", "type": "double"},
    "STR,END": {"name": "Стальной Вихрь", "type": "double"},
    "STR,TEC": {"name": "Техно-Левиафан", "type": "double"},
    "STR,DEF": {"name": "Бронебойный Титан", "type": "double"},
    "INT,END": {"name": "Ментальный Улей", "type": "double"},
    "INT,TEC": {"name": "Кибернетический Оракул", "type": "double"},
    "INT,DEF": {"name": "Щит Разума", "type": "double"},
    "END,TEC": {"name": "Нано-Резерв", "type": "double"},
    "END,DEF": {"name": "Вечный Улей", "type": "double"},
    "TEC,DEF": {"name": "Квантовый Барьер", "type": "double"},
    "STR,INT,END": {"name": "Триумвират Войны", "type": "triple"},
    "STR,INT,TEC": {"name": "Галактический Синтез", "type": "triple"},
    "STR,INT,DEF": {"name": "Алмазный Рассвет", "type": "triple"},
    "STR,END,TEC": {"name": "Кибер-Истребитель", "type": "triple"},
    "STR,END,DEF": {"name": "Непоколебимый Колосс", "type": "triple"},
    "STR,TEC,DEF": {"name": "Панцирь Прогресса", "type": "triple"},
    "INT,END,TEC": {"name": "Сеть Пандоры", "type": "triple"},
    "INT,END,DEF": {"name": "Фортрес Менталис", "type": "triple"},
    "INT,TEC,DEF": {"name": "Нейронный Кокон", "type": "triple"},
    "END,TEC,DEF": {"name": "Вечный Бастион", "type": "triple"}
}

tactics = {
    "Нейтральный Кодекс": {"attack": 0.5, "defense": 0.5},
    "Сокрушительный Натиск": {"attack": 1.0, "defense": 0.0},
    "Когнитивный Ураган": {"attack": 0.5, "defense": 0.5},
    "Неугасимый Феникс": {"attack": 0.25, "defense": 0.75},
    "Плазменный Импульс": {"attack": 0.75, "defense": 0.25},
    "Незыблемый Бастион": {"attack": 0.0, "defense": 1.0},
    "Тактический Кулак": {"attack": 0.75, "defense": 0.25},
    "Стальной Вихрь": {"attack": 0.5, "defense": 0.5},
    "Техно-Левиафан": {"attack": 0.81, "defense": 0.19},
    "Бронебойный Титан": {"attack": 0.33, "defense": 0.67},
    "Ментальный Улей": {"attack": 0.33, "defense": 0.67},
    "Кибернетический Оракул": {"attack": 0.69, "defense": 0.31},
    "Щит Разума": {"attack": 0.17, "defense": 0.83},
    "Нано-Резерв": {"attack": 0.55, "defense": 0.45},
    "Вечный Улей": {"attack": 0.13, "defense": 0.88},
    "Квантовый Барьер": {"attack": 0.45, "defense": 0.55},
    "Триумвират Войны": {"attack": 0.5, "defense": 0.5},
    "Галактический Синтез": {"attack": 0.75, "defense": 0.25},
    "Алмазный Рассвет": {"attack": 0.38, "defense": 0.63},
    "Кибер-Истребитель": {"attack": 0.63, "defense": 0.38},
    "Непоколебимый Колосс": {"attack": 0.3, "defense": 0.7},
    "Панцирь Прогресса": {"attack": 0.54, "defense": 0.46},
    "Сеть Пандоры": {"attack": 0.54, "defense": 0.46},
    "Фортрес Менталис": {"attack": 0.2, "defense": 0.8},
    "Нейронный Кокон": {"attack": 0.46, "defense": 0.54},
    "Вечный Бастион": {"attack": 0.39, "defense": 0.61}
}

def select_tactic(selected_skills):
    """Определяет тактику на основе выбранных скиллов и возвращает её параметры."""
    if not selected_skills:
        return "Нейтральный Кодекс", {"attack": 0.5, "defense": 0.5}

    key = ",".join(sorted(selected_skills))
    tactic_info = skill_to_tactic.get(key)

    if tactic_info:
        tactic_name = tactic_info["name"]
        return tactic_name, tactics.get(tactic_name, {"attack": 0.5, "defense": 0.5})

    # Если комбинация скиллов не найдена, возвращаем дефолт
    return "Нейтральный Кодекс", {"attack": 0.5, "defense": 0.5}
