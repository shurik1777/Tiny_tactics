import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    KeyboardButton, ReplyKeyboardMarkup
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token="7709218865:AAG8Ia1vo6TOMSQ0FD7HDEfGIc7pY0sBYoI")
dp = Dispatcher()
router = Router()


# Определение состояний для FSM
class BattleCalc(StatesGroup):
    selecting_attack_skills = State()
    selecting_defense_skills = State()
    selecting_attack_tactics = State()
    selecting_defense_tactics = State()
    selecting_achievements = State()
    calculating_result = State()


# Базовые значения скиллов
DEFAULT_SKILL_VALUE = 10
DEFAULT_MRL_VALUE = 10

# Словарь тактик с их параметрами атаки/защиты
tactics = {
    "Нейтральный Кодекс": {"attack": 0.5, "defense": 0.5},

    # Одиночные тактики
    "Сокрушительный Натиск": {"attack": 1.0, "defense": 0.0},
    "Когнитивный Ураган": {"attack": 0.5, "defense": 0.5},
    "Неугасимый Феникс": {"attack": 0.25, "defense": 0.75},
    "Плазменный Импульс": {"attack": 0.75, "defense": 0.25},
    "Незыблемый Бастион": {"attack": 0.0, "defense": 1.0},

    # Двойные тактики
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

    # Тройные тактики
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

# Маппинг выбора скиллов к тактикам
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

# Ачивки с их бонусами
achievements = {
    "Устал, но держусь! 1": {"DEF": 1},
    "Устал, но держусь! 2": {"DEF": 3},
    "Устал, но держусь! 3": {"DEF": 6},
    "Задира 1": {"defense_bonus": 0.03},
    "Задира 2": {"defense_bonus": 0.05},
    "Задира 3": {"defense_bonus": 0.10},
    "Домосед 1": {"attack_bonus": 0.02},
    "Домосед 2": {"attack_bonus": 0.04},
    "Домосед 3": {"attack_bonus": 0.07},
    "Пуленепробиваемый 1": {"attack_bonus": 0.03, "defense_bonus": 0.03},
    "Пуленепробиваемый 2": {"attack_bonus": 0.05, "defense_bonus": 0.05},
    "Пуленепробиваемый 3": {"attack_bonus": 0.10, "defense_bonus": 0.10}
}


# Создаем кнопки для скиллов
def create_skill_value_keyboard(skill_name):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    row = []

    for value in range(1, 101):
        if value % 10 == 1:  # Начинаем новый ряд каждые 10 значений
            if row:
                keyboard.inline_keyboard.append(row)
            row = []

        row.append(InlineKeyboardButton(
            text=str(value),
            callback_data=f"skill_{skill_name}_{value}"
        ))

    if row:
        keyboard.inline_keyboard.append(row)

    return keyboard


# Создаем кнопки для MRL
def create_mrl_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    row = []

    for value in range(1, 21):  # MRL от 1 до 20
        if value % 5 == 1:  # Начинаем новый ряд каждые 5 значений
            if row:
                keyboard.inline_keyboard.append(row)
            row = []

        row.append(InlineKeyboardButton(
            text=str(value),
            callback_data=f"mrl_{value}"
        ))

    if row:
        keyboard.inline_keyboard.append(row)

    return keyboard


# Создаем кнопки для выбора тактики
def create_tactics_keyboard(selected_skills):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    # Сортируем выбранные скиллы для получения правильного ключа
    selected_skills.sort()
    skill_key = ",".join(selected_skills)

    if skill_key in skill_to_tactic:
        tactic_name = skill_to_tactic[skill_key]["name"]
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=tactic_name,
                callback_data=f"tactic_{tactic_name}"
            )
        ])
    else:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="Нейтральный Кодекс",
                callback_data="tactic_Нейтральный Кодекс"
            )
        ])

    return keyboard


# Создаем кнопки для выбора ачивок
def create_achievements_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for achievement_name in achievements.keys():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=achievement_name,
                callback_data=f"achievement_{achievement_name}"
            )
        ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="Завершить выбор ачивок",
            callback_data="finish_achievements"
        )
    ])

    return keyboard


# Расчет результата сражения
def calculate_battle_result(attacker, defender):
    # Рассчитываем силу атаки
    attack_str = attacker["STR"] * (attacker["MRL"] / 10)
    attack_int = attacker["INT"] * (attacker["MRL"] / 10)
    attack_end = attacker["END"] * (attacker["MRL"] / 10)
    attack_tec = attacker["TEC"] * (attacker["MRL"] / 10)
    attack_def = attacker["DEF"] * (attacker["MRL"] / 10)

    attack_power = (attack_str + attack_int + attack_end + attack_tec + attack_def) * \
                   tactics[attacker["tactic"]]["attack"] * (1 + attacker.get("attack_bonus", 0))

    # Рассчитываем силу защиты
    defense_str = defender["STR"] * (defender["MRL"] / 10)
    defense_int = defender["INT"] * (defender["MRL"] / 10)
    defense_end = defender["END"] * (defender["MRL"] / 10)
    defense_tec = defender["TEC"] * (defender["MRL"] / 10)
    defense_def = defender["DEF"] * (defender["MRL"] / 10)

    defense_power = (defense_str + defense_int + defense_end + defense_tec + defense_def) * \
                    tactics[defender["tactic"]]["defense"] * (1 + defender.get("defense_bonus", 0))

    # Определяем победителя
    if attack_power > defense_power:
        winner = "attacker"
        ratio = attack_power / defense_power
    else:
        winner = "defender"
        ratio = defense_power / attack_power

    # Рассчитываем потери популяции (упрощенная формула)
    population_loss = min(0.5, 1 / (ratio + 1)) * 100  # Процент потерь

    return {
        "winner": winner,
        "attack_power": attack_power,
        "defense_power": defense_power,
        "ratio": ratio,
        "population_loss": population_loss
    }


# Обработчики команд и колбэков
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    # Инициализация значений по умолчанию
    await state.update_data(
        attacker={"STR": DEFAULT_SKILL_VALUE, "INT": DEFAULT_SKILL_VALUE,
                  "END": DEFAULT_SKILL_VALUE, "TEC": DEFAULT_SKILL_VALUE,
                  "DEF": DEFAULT_SKILL_VALUE, "MRL": DEFAULT_MRL_VALUE,
                  "tactic": "Нейтральный Кодекс",
                  "selected_skills": [], "achievements": []},
        defender={"STR": DEFAULT_SKILL_VALUE, "INT": DEFAULT_SKILL_VALUE,
                  "END": DEFAULT_SKILL_VALUE, "TEC": DEFAULT_SKILL_VALUE,
                  "DEF": DEFAULT_SKILL_VALUE, "MRL": DEFAULT_MRL_VALUE,
                  "tactic": "Нейтральный Кодекс",
                  "selected_skills": [], "achievements": []}
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Настроить атакующего", callback_data="setup_attacker")
        ],
        [
            InlineKeyboardButton(text="Настроить защищающегося", callback_data="setup_defender")
        ],
        [
            InlineKeyboardButton(text="Рассчитать результат", callback_data="calculate_result")
        ]
    ])

    await message.answer(
        "Добро пожаловать в калькулятор сражений Tiny Verse!\n"
        "Выберите действие:",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "setup_attacker")
async def setup_attacker(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="STR", callback_data="set_attacker_STR"),
            InlineKeyboardButton(text="INT", callback_data="set_attacker_INT"),
            InlineKeyboardButton(text="END", callback_data="set_attacker_END")
        ],
        [
            InlineKeyboardButton(text="TEC", callback_data="set_attacker_TEC"),
            InlineKeyboardButton(text="DEF", callback_data="set_attacker_DEF"),
            InlineKeyboardButton(text="MRL", callback_data="set_attacker_MRL")
        ],
        [
            InlineKeyboardButton(text="Выбрать тактику", callback_data="select_attacker_tactic")
        ],
        [
            InlineKeyboardButton(text="Выбрать ачивки", callback_data="select_attacker_achievements")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        ]
    ])

    data = await state.get_data()
    attacker = data.get("attacker", {})

    stats_text = (
        f"Текущие характеристики атакующего:\n"
        f"STR: {attacker.get('STR', DEFAULT_SKILL_VALUE)}\n"
        f"INT: {attacker.get('INT', DEFAULT_SKILL_VALUE)}\n"
        f"END: {attacker.get('END', DEFAULT_SKILL_VALUE)}\n"
        f"TEC: {attacker.get('TEC', DEFAULT_SKILL_VALUE)}\n"
        f"DEF: {attacker.get('DEF', DEFAULT_SKILL_VALUE)}\n"
        f"MRL: {attacker.get('MRL', DEFAULT_MRL_VALUE)}\n"
        f"Тактика: {attacker.get('tactic', 'Нейтральный Кодекс')}\n"
        f"Ачивки: {', '.join(attacker.get('achievements', [])) or 'Нет'}"
    )

    await callback.message.edit_text(stats_text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(lambda c: c.data == "setup_defender")
async def setup_defender(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="STR", callback_data="set_defender_STR"),
            InlineKeyboardButton(text="INT", callback_data="set_defender_INT"),
            InlineKeyboardButton(text="END", callback_data="set_defender_END")
        ],
        [
            InlineKeyboardButton(text="TEC", callback_data="set_defender_TEC"),
            InlineKeyboardButton(text="DEF", callback_data="set_defender_DEF"),
            InlineKeyboardButton(text="MRL", callback_data="set_defender_MRL")
        ],
        [
            InlineKeyboardButton(text="Выбрать тактику", callback_data="select_defender_tactic")
        ],
        [
            InlineKeyboardButton(text="Выбрать ачивки", callback_data="select_defender_achievements")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        ]
    ])

    data = await state.get_data()
    defender = data.get("defender", {})

    stats_text = (
        f"Текущие характеристики защищающегося:\n"
        f"STR: {defender.get('STR', DEFAULT_SKILL_VALUE)}\n"
        f"INT: {defender.get('INT', DEFAULT_SKILL_VALUE)}\n"
        f"END: {defender.get('END', DEFAULT_SKILL_VALUE)}\n"
        f"TEC: {defender.get('TEC', DEFAULT_SKILL_VALUE)}\n"
        f"DEF: {defender.get('DEF', DEFAULT_SKILL_VALUE)}\n"
        f"MRL: {defender.get('MRL', DEFAULT_MRL_VALUE)}\n"
        f"Тактика: {defender.get('tactic', 'Нейтральный Кодекс')}\n"
        f"Ачивки: {', '.join(defender.get('achievements', [])) or 'Нет'}"
    )

    await callback.message.edit_text(stats_text, reply_markup=keyboard)
    await callback.answer()


# Обработчики для настройки скиллов атакующего
@router.callback_query(lambda c: c.data.startswith("set_attacker_"))
async def set_attacker_skill(callback: types.CallbackQuery, state: FSMContext):
    skill = callback.data.split("_")[2]

    if skill == "MRL":
        keyboard = create_mrl_keyboard()
        await callback.message.edit_text(f"Выберите значение MRL для атакующего:", reply_markup=keyboard)
    else:
        keyboard = create_skill_value_keyboard(skill)
        await callback.message.edit_text(f"Выберите значение {skill} для атакующего:", reply_markup=keyboard)

    await callback.answer()


# Обработчики для настройки скиллов защищающегося
@router.callback_query(lambda c: c.data.startswith("set_defender_"))
async def set_defender_skill(callback: types.CallbackQuery, state: FSMContext):
    skill = callback.data.split("_")[2]

    if skill == "MRL":
        keyboard = create_mrl_keyboard()
        await callback.message.edit_text(f"Выберите значение MRL для защищающегося:", reply_markup=keyboard)
    else:
        keyboard = create_skill_value_keyboard(skill)
        await callback.message.edit_text(f"Выберите значение {skill} для защищающегося:", reply_markup=keyboard)

    await callback.answer()


# Обработчики выбора значения скилла
@router.callback_query(lambda c: c.data.startswith("skill_"))
async def process_skill_value(callback: types.CallbackQuery, state: FSMContext):
    _, skill_name, value = callback.data.split("_")
    data = await state.get_data()

    # Определяем, для кого настраиваем скилл
    if callback.message.text.startswith("Выберите значение") and "атакующего" in callback.message.text:
        entity = "attacker"
    else:
        entity = "defender"

    entity_data = data.get(entity, {})
    entity_data[skill_name] = int(value)

    data[entity] = entity_data
    await state.update_data(data)

    # Возвращаемся к меню настройки
    if entity == "attacker":
        await setup_attacker(callback, state)
    else:
        await setup_defender(callback, state)


# Обработчики выбора значения MRL
@router.callback_query(lambda c: c.data.startswith("mrl_"))
async def process_mrl_value(callback: types.CallbackQuery, state: FSMContext):
    value = int(callback.data.split("_")[1])
    data = await state.get_data()

    # Определяем, для кого настраиваем MRL
    if callback.message.text.startswith("Выберите значение MRL для атакующего"):
        entity = "attacker"
    else:
        entity = "defender"

    entity_data = data.get(entity, {})
    entity_data["MRL"] = value

    data[entity] = entity_data
    await state.update_data(data)

    # Возвращаемся к меню настройки
    if entity == "attacker":
        await setup_attacker(callback, state)
    else:
        await setup_defender(callback, state)


# Обработчики выбора тактики
@router.callback_query(lambda c: c.data == "select_attacker_tactic" or c.data == "select_defender_tactic")
async def select_tactic(callback: types.CallbackQuery, state: FSMContext):
    entity = "attacker" if "attacker" in callback.data else "defender"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="STR", callback_data=f"tactic_{entity}_STR"),
            InlineKeyboardButton(text="INT", callback_data=f"tactic_{entity}_INT"),
            InlineKeyboardButton(text="END", callback_data=f"tactic_{entity}_END")
        ],
        [
            InlineKeyboardButton(text="TEC", callback_data=f"tactic_{entity}_TEC"),
            InlineKeyboardButton(text="DEF", callback_data=f"tactic_{entity}_DEF")
        ],
        [
            InlineKeyboardButton(text="Завершить выбор", callback_data=f"finish_tactic_{entity}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"setup_{entity}")
        ]
    ])

    data = await state.get_data()
    entity_data = data.get(entity, {})
    selected_skills = entity_data.get("selected_skills", [])

    await callback.message.edit_text(
        f"Выберите скиллы для тактики {entity}:\n"
        f"Текущий выбор: {', '.join(selected_skills) or 'Нет'}\n"
        f"(Можно выбрать до 3 скиллов)",
        reply_markup=keyboard
    )
    await callback.answer()


# Обработчики выбора скилла для тактики
@router.callback_query(lambda c: c.data.startswith("tactic_attacker_") or c.data.startswith("tactic_defender_"))
async def select_tactic_skill(callback: types.CallbackQuery, state: FSMContext):
    _, entity, skill = callback.data.split("_")

    data = await state.get_data()
    entity_data = data.get(entity, {})
    selected_skills = entity_data.get("selected_skills", [])

    if skill in selected_skills:
        selected_skills.remove(skill)
    else:
        if len(selected_skills) < 3:  # Максимум 3 скилла
            selected_skills.append(skill)

    entity_data["selected_skills"] = selected_skills
    data[entity] = entity_data
    await state.update_data(data)

    # Обновляем сообщение
    await select_tactic(callback, state)


# Обработчики завершения выбора тактики
@router.callback_query(lambda c: c.data.startswith("finish_tactic_"))
async def finish_tactic_selection(callback: types.CallbackQuery, state: FSMContext):
    entity = callback.data.split("_")[2]

    data = await state.get_data()
    entity_data = data.get(entity, {})
    selected_skills = entity_data.get("selected_skills", [])

    # Сортируем выбранные скиллы для получения правильного ключа
    selected_skills.sort()
    skill_key = ",".join(selected_skills)

    if skill_key in skill_to_tactic:
        tactic_name = skill_to_tactic[skill_key]["name"]
        entity_data["tactic"] = tactic_name
    else:
        entity_data["tactic"] = "Нейтральный Кодекс"

    data[entity] = entity_data
    await state.update_data(data)

    # Возвращаемся к меню настройки
    if entity == "attacker":
        await setup_attacker(callback, state)
    else:
        await setup_defender(callback, state)


# Обработчики выбора ачивок
@router.callback_query(lambda c: c.data == "select_attacker_achievements" or c.data == "select_defender_achievements")
async def select_achievements(callback: types.CallbackQuery, state: FSMContext):
    entity = "attacker" if "attacker" in callback.data else "defender"

    keyboard = create_achievements_keyboard()

    data = await state.get_data()
    entity_data = data.get(entity, {})
    selected_achievements = entity_data.get("achievements", [])

    await callback.message.edit_text(
        f"Выберите ачивки для {entity}:\n"
        f"Текущий выбор: {', '.join(selected_achievements) or 'Нет'}",
        reply_markup=keyboard
    )
    await callback.answer()


# Обработчики выбора ачивки
@router.callback_query(lambda c: c.data.startswith("achievement_"))
async def select_achievement(callback: types.CallbackQuery, state: FSMContext):
    achievement_name = callback.data.split("_", 1)[1]

    # Определяем, для кого выбираем ачивку
    if "атакующего" in callback.message.text:
        entity = "attacker"
    else:
        entity = "defender"

    data = await state.get_data()
    entity_data = data.get(entity, {})
    selected_achievements = entity_data.get("achievements", [])

    if achievement_name in selected_achievements:
        selected_achievements.remove(achievement_name)
    else:
        selected_achievements.append(achievement_name)

    entity_data["achievements"] = selected_achievements

    # Применяем бонусы от ачивок
    attack_bonus = 0
    defense_bonus = 0

    for achievement in selected_achievements:
        if achievement in achievements:
            achievement_data = achievements[achievement]

            # Добавляем бонусы к скиллам
            for skill, value in achievement_data.items():
                if skill in ["STR", "INT", "END", "TEC", "DEF"]:
                    entity_data[skill] = entity_data.get(skill, DEFAULT_SKILL_VALUE) + value

            # Добавляем процентные бонусы
            attack_bonus += achievement_data.get("attack_bonus", 0)
            defense_bonus += achievement_data.get("defense_bonus", 0)

    entity_data["attack_bonus"] = attack_bonus
    entity_data["defense_bonus"] = defense_bonus

    data[entity] = entity_data
    await state.update_data(data)

    # Обновляем сообщение
    await select_achievements(callback, state)


# Обработчик завершения выбора ачивок
@router.callback_query(lambda c: c.data == "finish_achievements")
async def finish_achievements_selection(callback: types.CallbackQuery, state: FSMContext):
    # Определяем, для кого завершаем выбор ачивок
    if "атакующего" in callback.message.text:
        entity = "attacker"
        await setup_attacker(callback, state)
    else:
        entity = "defender"
        await setup_defender(callback, state)


# Обработчик возврата в главное меню
@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Настроить атакующего", callback_data="setup_attacker")
        ],
        [
            InlineKeyboardButton(text="Настроить защищающегося", callback_data="setup_defender")
        ],
        [
            InlineKeyboardButton(text="Рассчитать результат", callback_data="calculate_result")
        ]
    ])

    await callback.message.edit_text(
        "Калькулятор сражений Tiny Verse\n"
        "Выберите действие:",
        reply_markup=keyboard
    )
    await callback.answer()


# Обработчик расчета результата
@router.callback_query(lambda c: c.data == "calculate_result")
async def calculate_result(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    attacker = data.get("attacker", {})
    defender = data.get("defender", {})

    # Проверяем, что все необходимые данные заполнены
    if not all([attacker.get(skill) for skill in ["STR", "INT", "END", "TEC", "DEF", "MRL"]]) or \
            not all([defender.get(skill) for skill in ["STR", "INT", "END", "TEC", "DEF", "MRL"]]):
        await callback.message.edit_text(
            "Не все характеристики заполнены. Пожалуйста, заполните все необходимые данные.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Назад", callback_data="back_to_main")
            ]])
        )
        await callback.answer()
        return

    # Рассчитываем результат
    result = calculate_battle_result(attacker, defender)

    # Формируем сообщение с результатом
    if result["winner"] == "attacker":
        winner_text = "Атакующий побеждает!"
    else:
        winner_text = "Защищающийся побеждает!"

    result_text = (
        f"Результат сражения:\n\n"
        f"{winner_text}\n\n"
        f"Сила атаки: {result['attack_power']:.2f}\n"
        f"Сила защиты: {result['defense_power']:.2f}\n"
        f"Соотношение сил: 1:{result['ratio']:.2f}\n"
        f"Потери популяции: {result['population_loss']:.2f}%\n\n"
        f"Использованные тактики:\n"
        f"Атакующий: {attacker['tactic']}\n"
        f"Защищающийся: {defender['tactic']}"
    )

    await callback.message.edit_text(
        result_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        ]])
    )
    await callback.answer()


# Запуск бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
