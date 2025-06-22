# keyboards/builders.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_main_menu_keyboard():
    """Создает клавиатуру для главного меню."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Настроить атакующего", callback_data="setup_attacker")],
        [InlineKeyboardButton(text="Настроить защищающегося", callback_data="setup_defender")],
        [InlineKeyboardButton(text="Рассчитать результат", callback_data="calculate_result")],
    ])
    return keyboard


def create_skill_selection_keyboard(skill_name):
    """Создает клавиатуру для выбора значения скилла."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for i in range(1, 101):  # Диапазон значений от 1 до 100
        if i % 10 == 1:  # Новый ряд каждые 10 значений
            keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard[-1].append(InlineKeyboardButton(
            text=str(i), callback_data=f"set_skill_{skill_name}_{i}"
        ))
    return keyboard


def create_achievement_selection_keyboard(achievements, selected_achievements):
    """Создает клавиатуру для выбора ачивок."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for achievement in achievements:
        checkbox = "✅" if achievement in selected_achievements else "🔲"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{checkbox} {achievement}", callback_data=f"toggle_achievement_{achievement}"
            )
        ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Завершить выбор ачивок", callback_data="finish_achievements")
    ])
    return keyboard


def create_tactic_selection_keyboard(tactics, selected_tactics):
    """Создает клавиатуру для выбора тактики."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for tactic in tactics:
        checkbox = "✅" if tactic in selected_tactics else "🔲"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{checkbox} {tactic}", callback_data=f"toggle_tactic_{tactic}"
            )
        ])
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Завершить выбор тактики", callback_data="finish_tactics")
    ])
    return keyboard


def create_confirm_keyboard(confirm_callback, cancel_callback):
    """Создает клавиатуру для подтверждения действий."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=confirm_callback)],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_callback)]
    ])
    return keyboard
