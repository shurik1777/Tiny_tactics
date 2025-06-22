# app/handlers.py
import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.builders import create_main_menu_keyboard, create_tactic_selection_keyboard
from database.db_operations import load_user_data, save_user_data
from logic.state_management import select_tactic
from logic.calculations import calculate_battle_result
import logging

logger = logging.getLogger(__name__)
router = Router()


def setup_handlers(dp):
    dp.include_router(router)


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"User {user_id} started the bot.")

    # Загружаем данные пользователя или инициализируем их
    attacker_data, defender_data = await load_user_data(user_id)
    if not attacker_data or not defender_data:
        attacker_data = {
            "STR": 10, "INT": 10, "END": 10, "TEC": 10, "DEF": 10, "MRL": 10,
            "tactic": "Нейтральный Кодекс", "selected_skills": [], "achievements": []
        }
        defender_data = {
            "STR": 10, "INT": 10, "END": 10, "TEC": 10, "DEF": 10, "MRL": 10,
            "tactic": "Нейтральный Кодекс", "selected_skills": [], "achievements": []
        }
        await save_user_data(user_id, attacker_data, defender_data)

    await state.set_data({"attacker": attacker_data, "defender": defender_data})
    keyboard = create_main_menu_keyboard()
    await message.answer("Добро пожаловать в калькулятор сражений! Выберите действие:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data in ["setup_attacker", "setup_defender"])
async def setup_entity(callback: types.CallbackQuery, state: FSMContext):
    entity = "attacker" if callback.data == "setup_attacker" else "defender"
    data = await state.get_data()
    entity_data = data.get(entity, {})

    # Формируем текст и клавиатуру
    keyboard = create_tactic_selection_keyboard(["Нейтральный Кодекс", "Сокрушительный Натиск", "Когнитивный Ураган"],
                                                [entity_data.get("tactic")])
    stats_text = (
        f"⚔️ Текущие характеристики {entity}:\n"
        f"STR: {entity_data.get('STR', 0)}\n"
        f"INT: {entity_data.get('INT', 0)}\n"
        f"END: {entity_data.get('END', 0)}\n"
        f"TEC: {entity_data.get('TEC', 0)}\n"
        f"DEF: {entity_data.get('DEF', 0)}\n"
        f"MRL: {entity_data.get('MRL', 0)}\n"
        f"Тактика: {entity_data.get('tactic', 'Не выбрано')}\n"
        f"Ачивки: {', '.join(entity_data.get('achievements', [])) or 'Нет'}"
    )

    await callback.message.edit_text(stats_text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(lambda c: c.data == "calculate_result")
async def calculate_result_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    attacker = data.get("attacker")
    defender = data.get("defender")

    if not attacker or not defender:
        logger.warning(f"Данные FSM отсутствуют. Загружаем из базы для пользователя {user_id}.")
        attacker, defender = await load_user_data(user_id)

    if not attacker or not defender:
        await callback.message.edit_text("Ошибка: не удалось загрузить данные для расчета.")
        await callback.answer()
        return

    logger.info(f"Данные атакующего: {attacker}, Данные защищающегося: {defender}")

    result = calculate_battle_result(attacker, defender)

    result_text = (
        f"📊 Результат сражения!\n\n"
        f"🎉 {result['winner'].capitalize()} побеждает! 🎉\n\n"
        f"⚔️ Сила атаки: {result['attack_power']}\n"
        f"🛡️ Сила защиты: {result['defense_power']}\n"
        f"🔢 Соотношение сил: 1:{round(result['attack_power'] / result['defense_power'], 2)}\n"
        f"💔 Потери популяции: {result['population_loss']}%\n\n"
        f"✨ Использованные тактики:\n"
        f"Атакующий: {attacker['tactic']}\n"
        f"Защищающийся: {defender['tactic']}"
    )

    # Отправляем результат с кнопкой очистки
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Очистить результат", callback_data="clear_result")]
    ])

    await callback.message.edit_text(result_text, reply_markup=keyboard)

    await asyncio.sleep(0.5)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("select_tactic_"))
async def select_tactic_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора тактики с накопительным подходом."""
    tactic_name = callback.data.split("_")[2]  # Извлекаем название тактики из callback_data
    user_id = callback.from_user.id

    # Загружаем данные FSM
    data = await state.get_data()
    entity = "attacker" if "attacker" in data else "defender"
    entity_data = data.get(entity, {})

    # Обновляем тактику
    previous_tactic = entity_data.get("tactic", "Не выбрано")
    entity_data["tactic"] = tactic_name

    # Обновляем данные в FSM
    await state.update_data({entity: entity_data})

    # Сохраняем изменения в базе данных и дожидаемся завершения операции
    if entity == "attacker":
        await save_user_data(user_id, entity_data, data.get("defender", {}))
    else:
        await save_user_data(user_id, data.get("attacker", {}), entity_data)

    # Логирование изменений
    logger.info(f"Тактика для {entity} обновлена с {previous_tactic} на {tactic_name}. Текущие данные: {entity_data}")

    # Уведомление пользователя
    await callback.message.edit_text(
        f"Тактика обновлена: {tactic_name}\n"
        f"Теперь вы можете выбрать или изменить другие настройки.",
        reply_markup=None  # Отключаем клавиатуру после выбора
    )
    await asyncio.sleep(0.5)  # Задержка для стабильности обработки

    await callback.answer("Выбор тактики обработан.")

