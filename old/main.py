import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


# Импортируем наш модуль для работы с базой данных
import database

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Добавил формат
logger = logging.getLogger(__name__)  # Используем logger, а не print

# Инициализация бота и диспетчера
bot = Bot(token="7709218865:AAG8Ia1vo6TOMSQ0FD7HDEfGIc7pY0sBYoI")
dp = Dispatcher()
router = Router()


# Определение состояний для FSM (используются для потока, но не для хранения данных между запусками)
class BattleCalc(StatesGroup):
    # Эти состояния не используются напрямую для навигации, но оставлены как структура
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
    "Нейтральный Кодекс": {"attack_multiplier": 0.5, "defense_multiplier": 0.5},  # Изменил ключи для ясности

    # Одиночные тактики
    "Сокрушительный Натиск": {"attack_multiplier": 1.0, "defense_multiplier": 0.0},
    "Когнитивный Ураган": {"attack_multiplier": 0.5, "defense_multiplier": 0.5},
    "Неугасимый Феникс": {"attack_multiplier": 0.25, "defense_multiplier": 0.75},
    "Плазменный Импульс": {"attack_multiplier": 0.75, "defense_multiplier": 0.25},
    "Незыблемый Бастион": {"attack_multiplier": 0.0, "defense_multiplier": 1.0},

    # Двойные тактики (ключи для удобства переименовал)
    "Тактический Кулак": {"attack_multiplier": 0.75, "defense_multiplier": 0.25},
    "Стальной Вихрь": {"attack_multiplier": 0.5, "defense_multiplier": 0.5},
    "Техно-Левиафан": {"attack_multiplier": 0.81, "defense_multiplier": 0.19},
    "Бронебойный Титан": {"attack_multiplier": 0.33, "defense_multiplier": 0.67},
    "Ментальный Улей": {"attack_multiplier": 0.33, "defense_multiplier": 0.67},
    "Кибернетический Оракул": {"attack_multiplier": 0.69, "defense_multiplier": 0.31},
    "Щит Разума": {"attack_multiplier": 0.17, "defense_multiplier": 0.83},
    "Нано-Резерв": {"attack_multiplier": 0.55, "defense_multiplier": 0.45},
    "Вечный Улей": {"attack_multiplier": 0.13, "defense_multiplier": 0.88},
    "Квантовый Барьер": {"attack_multiplier": 0.45, "defense_multiplier": 0.55},

    # Тройные тактики
    "Триумвират Войны": {"attack_multiplier": 0.5, "defense_multiplier": 0.5},
    "Галактический Синтез": {"attack_multiplier": 0.75, "defense_multiplier": 0.25},
    "Алмазный Рассвет": {"attack_multiplier": 0.38, "defense_multiplier": 0.63},
    "Кибер-Истребитель": {"attack_multiplier": 0.63, "defense_multiplier": 0.38},
    "Непоколебимый Колосс": {"attack_multiplier": 0.3, "defense_multiplier": 0.7},
    "Панцирь Прогресса": {"attack_multiplier": 0.54, "defense_multiplier": 0.46},
    "Сеть Пандоры": {"attack_multiplier": 0.54, "defense_multiplier": 0.46},
    "Фортрес Менталис": {"attack_multiplier": 0.2, "defense_multiplier": 0.8},
    "Нейронный Кокон": {"attack_multiplier": 0.46, "defense_multiplier": 0.54},
    "Вечный Бастион": {"attack_multiplier": 0.39, "defense_multiplier": 0.61}
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
    "Устал, но держусь! 1": {"DEF_bonus": 1},  # Добавил _bonus для direct skill bonuses
    "Устал, но держусь! 2": {"DEF_bonus": 3},
    "Устал, но держусь! 3": {"DEF_bonus": 6},
    "Задира 1": {"defense_pct_bonus": 0.03},  # Изменил ключи для ясности
    "Задира 2": {"defense_pct_bonus": 0.05},
    "Задира 3": {"defense_pct_bonus": 0.10},
    "Домосед 1": {"attack_pct_bonus": 0.02},
    "Домосед 2": {"attack_pct_bonus": 0.04},
    "Домосед 3": {"attack_pct_bonus": 0.07},
    "Пуленепробиваемый 1": {"attack_pct_bonus": 0.03, "defense_pct_bonus": 0.03},
    "Пуленепробиваемый 2": {"attack_pct_bonus": 0.05, "defense_pct_bonus": 0.05},
    "Пуленепробиваемый 3": {"attack_pct_bonus": 0.10, "defense_pct_bonus": 0.10}
}


# Создаем кнопки для скиллов
def create_skill_value_keyboard(skill_name):
    # Учитываем, что DEF может быть больше 100 из-за ачивок, но для выбора базового значения это неактуально
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    rows = []  # Используем list of lists для формирования рядов

    for value in range(1, 101):
        if (value - 1) % 10 == 0:  # Создаем новый ряд каждые 10 значений
            rows.append([])
        rows[-1].append(InlineKeyboardButton(text=str(value), callback_data=f"skill_{skill_name}_{value}"))

    keyboard.inline_keyboard = rows
    return keyboard


# Создаем кнопки для MRL
def create_mrl_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    rows = []

    for value in range(1, 21):  # MRL от 1 до 20
        if (value - 1) % 5 == 0:  # Начинаем новый ряд каждые 5 значений
            rows.append([])
        rows[-1].append(InlineKeyboardButton(text=str(value), callback_data=f"mrl_{value}"))

    keyboard.inline_keyboard = rows
    return keyboard


# Создаем кнопки для выбора тактики (отображает только выбранную/нейтральную)
def create_tactics_keyboard(selected_skills):
    # Эта функция больше не используется для выбора, тактика определяется автоматически
    # исходя из выбранных скиллов, которые указывают на тип тактики.
    # Так что она может быть упрощена или удалена, если тактику выбирают через скиллы.
    # В текущей логике, тактика выбирается автоматически по комбинации скиллов.
    pass


# Создаем кнопки для выбора ачивок
def create_achievements_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    # Динамически добавляем кнопки для каждой ачивки
    for achievement_name in achievements.keys():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=achievement_name,
                callback_data=f"select_achievement_{achievement_name}"  # Изменил callback_data для ясности
            )
        ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="Завершить выбор ачивок",
            callback_data="finish_achievements_current_entity"  # Изменил callback_data для ясности
        )
    ])

    return keyboard


# Расчет результата сражения
def calculate_battle_result(attacker_raw, defender_raw):
    # Функция для получения эффективных характеристик с учетом ачивок
    def get_effective_stats(entity_data_raw):
        effective_entity_data = entity_data_raw.copy()  # Копируем базовые данные

        # Обнуляем бонусы, которые будут накоплены из ачивок для текущего расчета
        effective_attack_pct_bonus = 0.0
        effective_defense_pct_bonus = 0.0

        # Применяем бонусы от выбранных ачивок
        for achievement_name in entity_data_raw.get("achievements", []):
            if achievement_name in achievements:
                ach_bonuses = achievements[achievement_name]

                # Применяем прямые бонусы к скиллам (например, DEF+1)
                for skill_key in ["STR", "INT", "END", "TEC", "DEF"]:
                    skill_bonus_key = f"{skill_key}_bonus"
                    if skill_bonus_key in ach_bonuses:
                        effective_entity_data[skill_key] += ach_bonuses[skill_bonus_key]

                # Накапливаем процентные бонусы
                effective_attack_pct_bonus += ach_bonuses.get("attack_pct_bonus", 0.0)
                effective_defense_pct_bonus += ach_bonuses.get("defense_pct_bonus", 0.0)

        # Сохраняем накопленные бонусы во временном словаре для использования в расчете
        effective_entity_data["total_attack_pct_bonus"] = effective_attack_pct_bonus
        effective_entity_data["total_defense_pct_bonus"] = effective_defense_pct_bonus

        return effective_entity_data

    # Получаем эффективные характеристики для атакующего и защищающегося
    attacker = get_effective_stats(attacker_raw)
    defender = get_effective_stats(defender_raw)

    # Рассчитываем силу атаки
    # Суммируем скиллы, умноженные на MRL/10, и применяем тактику и процентные бонусы
    summed_mrl_skills_attacker = (
                                         attacker["STR"] + attacker["INT"] + attacker["END"] + attacker["TEC"] +
                                         attacker["DEF"]
                                 ) * (attacker["MRL"] / 10)  # MRL применяется ко всей сумме скиллов

    attack_power = summed_mrl_skills_attacker * \
                   tactics[attacker["tactic"]]["attack_multiplier"] * (1 + attacker["total_attack_pct_bonus"])

    # Рассчитываем силу защиты
    summed_mrl_skills_defender = (
                                         defender["STR"] + defender["INT"] + defender["END"] + defender["TEC"] +
                                         defender["DEF"]
                                 ) * (defender["MRL"] / 10)

    defense_power = summed_mrl_skills_defender * \
                    tactics[defender["tactic"]]["defense_multiplier"] * (1 + defender["total_defense_pct_bonus"])

    # Определяем победителя
    if attack_power > defense_power:
        winner = "attacker"
        # Для удобства, соотношение всегда > 1, если победитель атакующий
        ratio = attack_power / defense_power
    elif defense_power > attack_power:
        winner = "defender"
        # Для удобства, соотношение всегда > 1, если победитель защищающийся
        ratio = defense_power / attack_power
    else:  # Если силы равны
        winner = "draw"
        ratio = 1.0

    # Рассчитываем потери популяции (упрощенная формула, как в оригинале)
    # Формула потерь: min(0.5, 1 / (ratio + 1)) * 100
    # Здесь ratio - это отношение силы победителя к силе проигравшего
    if winner == "draw":
        population_loss = 0  # Потери при ничьей 0
    else:
        # Для корректного подсчета потерь, ratio должен быть >= 1
        # Если attack_power > defense_power, ratio уже attack/defense
        # Если defense_power > attack_power, ratio уже defense/attack
        # Иначе losses будут считаться неверно.
        population_loss = min(0.5, 1 / (ratio + 0.5)) * 100  # Изменил формулу для более адекватных потерь

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
    user_id = message.from_user.id
    logger.info(f"User {user_id} started the bot.")

    # Загружаем данные пользователя из БД
    attacker_data, defender_data = database.load_user_data(user_id)

    # Инициализация значений по умолчанию, если данных нет
    if not attacker_data:
        logger.info(f"Initializing default attacker data for user {user_id}")
        attacker_data = {
            "STR": DEFAULT_SKILL_VALUE, "INT": DEFAULT_SKILL_VALUE,
            "END": DEFAULT_SKILL_VALUE, "TEC": DEFAULT_SKILL_VALUE,
            "DEF": DEFAULT_SKILL_VALUE, "MRL": DEFAULT_MRL_VALUE,
            "tactic": "Нейтральный Кодекс",
            "selected_skills": [],  # Скиллы, выбранные для определения тактики
            "achievements": []  # Список выбранных ачивок
        }
    if not defender_data:
        logger.info(f"Initializing default defender data for user {user_id}")
        defender_data = {
            "STR": DEFAULT_SKILL_VALUE, "INT": DEFAULT_SKILL_VALUE,
            "END": DEFAULT_SKILL_VALUE, "TEC": DEFAULT_SKILL_VALUE,
            "DEF": DEFAULT_SKILL_VALUE, "MRL": DEFAULT_MRL_VALUE,
            "tactic": "Нейтральный Кодекс",
            "selected_skills": [],
            "achievements": []
        }

    await state.set_data({
        "attacker": attacker_data,
        "defender": defender_data
    })
    # Сохраняем (или обновляем) данные в БД сразу после загрузки/инициализации
    database.save_user_data(user_id, attacker_data, defender_data)

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
    await state.set_state(None)  # Сброс состояния FSM, так как данные хранятся в БД


@router.callback_query(lambda c: c.data == "setup_attacker")
async def setup_attacker(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    attacker = data.get("attacker", {})  # Берем из FSM, там актуальные данные

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
            InlineKeyboardButton(text="Выбрать тактику (по скиллам)", callback_data="select_attacker_tactics_skills")
        ],
        [
            InlineKeyboardButton(text="Выбрать ачивки", callback_data="select_attacker_achievements")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        ]
    ])

    # Отображаем текущие базовые характеристики (без бонусов от ачивок)
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
    data = await state.get_data()
    defender = data.get("defender", {})  # Берем из FSM, там актуальные данные

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
            InlineKeyboardButton(text="Выбрать тактику (по скиллам)", callback_data="select_defender_tactics_skills")
        ],
        [
            InlineKeyboardButton(text="Выбрать ачивки", callback_data="select_defender_achievements")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        ]
    ])

    # Отображаем текущие базовые характеристики (без бонусов от ачивок)
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


# Обработчики для настройки скиллов
@router.callback_query(lambda c: c.data.startswith(("set_attacker_", "set_defender_")))
async def set_skill_value_prompt(callback: types.CallbackQuery, state: FSMContext):
    # Определяем, для кого настраивается скилл и какой именно скилл
    parts = callback.data.split("_")
    entity = parts[1]  # 'attacker' or 'defender'
    skill = parts[2]  # 'STR', 'INT', 'MRL', etc.

    if skill == "MRL":
        keyboard = create_mrl_keyboard()
        await callback.message.edit_text(
            f"Выберите значение MRL для {'атакующего' if entity == 'attacker' else 'защищающегося'}:",
            reply_markup=keyboard)
    else:
        keyboard = create_skill_value_keyboard(skill)
        await callback.message.edit_text(
            f"Выберите значение {skill} для {'атакующего' if entity == 'attacker' else 'защищающегося'}:",
            reply_markup=keyboard)

    await state.update_data({"current_entity_for_skill_set": entity})  # Запоминаем, для кого устанавливаем
    await callback.answer()


# Обработчики выбора значения скилла (STR, INT, END, TEC, DEF)
@router.callback_query(lambda c: c.data.startswith("skill_"))
async def process_skill_value(callback: types.CallbackQuery, state: FSMContext):
    _, skill_name, value_str = callback.data.split("_")
    value = int(value_str)

    fsm_data = await state.get_data()
    entity = fsm_data.get("current_entity_for_skill_set")  # Получаем из FSM, для кого устанавливали скилл

    if not entity:  # Защита от непредвиденных ситуаций
        await callback.answer("Ошибка: Не удалось определить, для кого менять скилл.", show_alert=True)
        await back_to_main(callback, state)
        return

    entity_data = fsm_data.get(entity, {}).copy()
    entity_data[skill_name] = value
    fsm_data[entity] = entity_data
    await state.update_data(fsm_data)
    database.save_user_data(callback.from_user.id, fsm_data["attacker"], fsm_data["defender"])  # Сохраняем в БД

    # Возвращаемся к меню настройки
    if entity == "attacker":
        await setup_attacker(callback, state)
    else:
        await setup_defender(callback, state)


# Обработчики выбора значения MRL
@router.callback_query(lambda c: c.data.startswith("mrl_"))
async def process_mrl_value(callback: types.CallbackQuery, state: FSMContext):
    value = int(callback.data.split("_")[1])

    fsm_data = await state.get_data()
    entity = fsm_data.get("current_entity_for_skill_set")  # Получаем из FSM, для кого устанавливали MRL

    if not entity:  # Защита от непредвиденных ситуаций
        await callback.answer("Ошибка: Не удалось определить, для кого менять MRL.", show_alert=True)
        await back_to_main(callback, state)
        return

    entity_data = fsm_data.get(entity, {}).copy()
    entity_data["MRL"] = value
    fsm_data[entity] = entity_data
    await state.update_data(fsm_data)
    database.save_user_data(callback.from_user.id, fsm_data["attacker"], fsm_data["defender"])  # Сохраняем в БД

    # Возвращаемся к меню настройки
    if entity == "attacker":
        await setup_attacker(callback, state)
    else:
        await setup_defender(callback, state)


# Обработчики выбора тактики по скиллам
@router.callback_query(
    lambda c: c.data == "select_attacker_tactics_skills" or c.data == "select_defender_tactics_skills")
async def select_tactics_skills(callback: types.CallbackQuery, state: FSMContext):
    entity = "attacker" if "attacker" in callback.data else "defender"
    await state.update_data({"current_entity_for_tactic_set": entity})  # Запоминаем, для кого выбираем тактику

    data = await state.get_data()
    entity_data = data.get(entity, {})
    selected_skills = entity_data.get("selected_skills", [])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{'🔲' if 'STR' not in selected_skills else '✅'} STR",
                              callback_data=f"tactic_skill_STR")],
        [InlineKeyboardButton(text=f"{'🔲' if 'INT' not in selected_skills else '✅'} INT",
                              callback_data=f"tactic_skill_INT")],
        [InlineKeyboardButton(text=f"{'🔲' if 'END' not in selected_skills else '✅'} END",
                              callback_data=f"tactic_skill_END")],
        [InlineKeyboardButton(text=f"{'🔲' if 'TEC' not in selected_skills else '✅'} TEC",
                              callback_data=f"tactic_skill_TEC")],
        [InlineKeyboardButton(text=f"{'🔲' if 'DEF' not in selected_skills else '✅'} DEF",
                              callback_data=f"tactic_skill_DEF")],
        [InlineKeyboardButton(text="Завершить выбор тактики", callback_data="finish_tactic_selection")]
    ])

    await callback.message.edit_text(
        f"Выберите скиллы для тактики {'атакующего' if entity == 'attacker' else 'защищающегося'}:\n"
        f"Текущий выбор: {', '.join(selected_skills) or 'Нет'}\n"
        f"(Можно выбрать до 3 скиллов. Тактика определится автоматически)",
        reply_markup=keyboard
    )
    await callback.answer()


# Обработчики выбора скилла для тактики (чекбокс)
@router.callback_query(lambda c: c.data.startswith("tactic_skill_"))
async def toggle_tactic_skill(callback: types.CallbackQuery, state: FSMContext):
    skill = callback.data.split("_")[2]

    fsm_data = await state.get_data()
    entity = fsm_data.get("current_entity_for_tactic_set")

    if not entity:
        await callback.answer("Ошибка: Не удалось определить, для кого выбирать тактику.", show_alert=True)
        await back_to_main(callback, state)
        return

    entity_data = fsm_data.get(entity, {}).copy()
    selected_skills = entity_data.get("selected_skills", [])

    if skill in selected_skills:
        selected_skills.remove(skill)
    else:
        if len(selected_skills) < 3:  # Максимум 3 скилла
            selected_skills.append(skill)
        else:
            await callback.answer("Вы можете выбрать не более 3 скиллов для тактики.", show_alert=True)
            return

    entity_data["selected_skills"] = selected_skills
    fsm_data[entity] = entity_data
    await state.update_data(fsm_data)
    # Сохранение в БД произойдет при завершении выбора тактики

    # Обновляем сообщение (для отображения чекбоксов)
    await select_tactics_skills(callback, state)  # Перезапускаем отображение кнопок


# Обработчики завершения выбора тактики
@router.callback_query(lambda c: c.data == "finish_tactic_selection")
async def finish_tactic_selection(callback: types.CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    entity = fsm_data.get("current_entity_for_tactic_set")

    if not entity:
        await callback.answer("Ошибка: Не удалось определить, для кого назначить тактику.", show_alert=True)
        await back_to_main(callback, state)
        return

    entity_data = fsm_data.get(entity, {}).copy()
    selected_skills = entity_data.get("selected_skills", [])

    # Сортируем выбранные скиллы для получения правильного ключа
    selected_skills.sort()
    skill_key = ",".join(selected_skills)

    if skill_key in skill_to_tactic:
        tactic_name = skill_to_tactic[skill_key]["name"]
        entity_data["tactic"] = tactic_name
    else:
        entity_data["tactic"] = "Нейтральный Кодекс"  # Если комбинации нет или выбрано 0 скиллов

    fsm_data[entity] = entity_data
    await state.update_data(fsm_data)
    database.save_user_data(callback.from_user.id, fsm_data["attacker"], fsm_data["defender"])  # Сохраняем в БД

    # Возвращаемся к меню настройки
    if entity == "attacker":
        await setup_attacker(callback, state)
    else:
        await setup_defender(callback, state)


# Обработчики выбора ачивок
@router.callback_query(lambda c: c.data == "select_attacker_achievements" or c.data == "select_defender_achievements")
async def select_achievements_menu(callback: types.CallbackQuery, state: FSMContext):
    entity = "attacker" if "attacker" in callback.data else "defender"
    await state.update_data({"current_entity_for_achievement_set": entity})  # Запоминаем, для кого выбираем ачивки

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    data = await state.get_data()
    entity_data = data.get(entity, {})
    selected_achievements = entity_data.get("achievements", [])

    # Динамически генерируем кнопки с чекбоксами
    for achievement_name in achievements.keys():
        checkbox = "✅" if achievement_name in selected_achievements else "🔲"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{checkbox} {achievement_name}",
                callback_data=f"toggle_achievement_{achievement_name}"  # Изменил callback_data
            )
        ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="Завершить выбор ачивок",
            callback_data="finish_achievements_current_entity"  # Изменил callback_data
        )
    ])

    await callback.message.edit_text(
        f"Выберите ачивки для {'атакующего' if entity == 'attacker' else 'защищающегося'}:\n"
        f"Текущий выбор: {', '.join(selected_achievements) or 'Нет'}",
        reply_markup=keyboard
    )
    await callback.answer()


# Обработчики переключения ачивки (постановка/снятие чекбокса)
@router.callback_query(lambda c: c.data.startswith("toggle_achievement_"))
async def toggle_achievement(callback: types.CallbackQuery, state: FSMContext):
    achievement_name = callback.data.split("_", 2)[2]  # Извлекаем имя ачивки

    fsm_data = await state.get_data()
    entity = fsm_data.get("current_entity_for_achievement_set")

    if not entity:
        await callback.answer("Ошибка: Не удалось определить, для кого переключать ачивку.", show_alert=True)
        await back_to_main(callback, state)
        return

    entity_data = fsm_data.get(entity, {}).copy()
    selected_achievements = entity_data.get("achievements", [])

    if achievement_name in selected_achievements:
        selected_achievements.remove(achievement_name)
    else:
        selected_achievements.append(achievement_name)  # Можно добавить лимит на количество ачивок, если нужно

    entity_data["achievements"] = selected_achievements
    fsm_data[entity] = entity_data
    await state.update_data(fsm_data)
    # Сохранение в БД произойдет при завершении выбора, а не при каждом переключении
    # чтобы избежать частых обращений к БД и лишних расчетов бонусов (ведь для FSM-контекста они не нужны здесь)

    # Обновляем сообщение для отображения нового состояния чекбокса
    await select_achievements_menu(callback, state)


# Обработчик завершения выбора ачивок
@router.callback_query(lambda c: c.data == "finish_achievements_current_entity")
async def finish_achievements_selection(callback: types.CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    entity = fsm_data.get("current_entity_for_achievement_set")

    if not entity:  # Защита от непредвиденных ситуаций
        await callback.answer("Ошибка: Не удалось определить, для кого завершать выбор ачивок.", show_alert=True)
        await back_to_main(callback, state)
        return

    # Сохраняем последнее состояние ачивок в БД
    database.save_user_data(callback.from_user.id, fsm_data["attacker"], fsm_data["defender"])

    # Возвращаемся в меню настройки соответствующего персонажа
    if entity == "attacker":
        await setup_attacker(callback, state)
    else:
        await setup_defender(callback, state)


# Обработчик возврата в главное меню
@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    # Обновляем FSM Context данными из БД на случай, если что-то изменилось вне этого потока
    user_id = callback.from_user.id
    attacker_data, defender_data = database.load_user_data(user_id)
    if attacker_data and defender_data:
        await state.set_data({"attacker": attacker_data, "defender": defender_data})
    else:  # Это не должно происходить после первого запуска
        logger.warning(f"No existing data for user {user_id} when returning to main menu.")
        await cmd_start(callback.message, state)  # Перезапустить с нуля, если нет данных

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
        "Калькулятор сражений Tiny Verse.\n"
        "Выберите действие:",
        reply_markup=keyboard
    )
    await callback.answer()
    await state.set_state(None)  # Сброс текущего FSM состояния


# Обработчик расчета результата
@router.callback_query(lambda c: c.data == "calculate_result")
async def calculate_result(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BattleCalc.calculating_result)  # Устанавливаем состояние для ясности

    # Загружаем самые актуальные данные из FSMContext (они уже синхронизированы с БД)
    # Если данные в FSMContext устарели по какой-то причине, можно загрузить их снова из БД
    user_id = callback.from_user.id
    attacker, defender = database.load_user_data(user_id)

    if not attacker or not defender:
        await callback.message.edit_text(
            "Ошибка: Не удалось загрузить данные для расчета. Пожалуйста, начните заново.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Назад", callback_data="back_to_main")
            ]])
        )
        await callback.answer()
        return

    # Проверяем, что все необходимые данные заполнены
    # (скиллы должны быть словарями, а MRL - числом)
    required_skills = ["STR", "INT", "END", "TEC", "DEF", "MRL"]

    if not all(skill in attacker and isinstance(attacker[skill], (int, float)) for skill in required_skills) or \
            not all(skill in defender and isinstance(defender[skill], (int, float)) for skill in required_skills):
        await callback.message.edit_text(
            "Не все характеристики заполнены или имеют неверный формат. Пожалуйста, заполните все необходимые данные корректно, прежде чем рассчитывать.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Назад", callback_data="back_to_main")
            ]])
        )
        await callback.answer()
        return

    # Выполняем расчет
    result = calculate_battle_result(attacker, defender)

    # Формируем сообщение с результатом
    winner_text = ""
    if result["winner"] == "attacker":
        winner_text = "🎉 Атакующий побеждает! 🎉"
    elif result["winner"] == "defender":
        winner_text = "🛡️ Защищающийся побеждает! 🛡️"
    else:  # "draw"
        winner_text = "🤝 Ничья! 🤝"

    result_text = (
        f"📈 Результат сражения! 📊\n\n"
        f"{winner_text}\n\n"
        f"⚔️ Сила атаки: {result['attack_power']:.2f}\n"
        f"🛡️ Сила защиты: {result['defense_power']:.2f}\n"
        f"🔢 Соотношение сил: 1:{result['ratio']:.2f}\n"
        f"💔 Потери популяции: {result['population_loss']:.2f}%\n\n"
        f"✨ Использованные тактики:\n"
        f"Атакующий: {attacker['tactic']}\n"
        f"Защищающийся: {defender['tactic']}"
    )

    await callback.message.edit_text(
        result_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🚀 Новое сражение", callback_data="back_to_main")
        ]])
    )
    await callback.answer()
    await state.set_state(None)  # Сброс состояния после расчета


# Запуск бота
async def main():
    logger.info("Starting bot...")
    database.init_db()  # Инициализируем базу данных при запуске
    dp.include_router(router)
    await dp.start_polling(bot)
    logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
