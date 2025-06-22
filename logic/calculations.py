from logic.state_management import tactics  # Используем общий словарь тактик

def calculate_battle_result(attacker, defender):
    """Рассчитывает результат сражения между атакующим и защищающимся."""

    def calculate_effective_power(entity, tactic_name):
        """Вычисляет силу атаки и защиты с учетом выбранной тактики."""
        base_power = sum(entity[skill] for skill in ["STR", "INT", "END", "TEC", "DEF"])
        tactic_params = tactics.get(tactic_name, {"attack": 0.5, "defense": 0.5})
        effective_attack = base_power * tactic_params["attack"] * (entity["MRL"] / 10)
        effective_defense = base_power * tactic_params["defense"] * (entity["MRL"] / 10)
        return effective_attack, effective_defense

    # Получаем тактики для атакующего и защищающегося
    attacker_tactic = attacker.get("tactic", "Нейтральный Кодекс")
    defender_tactic = defender.get("tactic", "Нейтральный Кодекс")

    # Считаем силы атаки и защиты
    attack_power, _ = calculate_effective_power(attacker, attacker_tactic)
    _, defense_power = calculate_effective_power(defender, defender_tactic)

    # Определяем победителя
    if attack_power > defense_power:
        winner = "attacker"
    elif defense_power > attack_power:
        winner = "defender"
    else:
        winner = "draw"

    # Рассчитываем потери популяции
    population_loss = min(0.5, abs(attack_power - defense_power) / max(attack_power, defense_power)) * 100

    return {
        "winner": winner,
        "attack_power": round(attack_power, 2),
        "defense_power": round(defense_power, 2),
        "population_loss": round(population_loss, 2)
    }
