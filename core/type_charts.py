# DEFENSE_CHART: Effektivität gegnerischer Angriffe auf diesen Typ
DEFENSE_CHART = {
    "normal":    {"fighting": 2, "ghost": 0, "steel": 0.5},
    "fire":      {"water": 2, "ground": 2, "rock": 2, "fire": 0.5, "grass": 0.5, "ice": 0.5, "bug": 0.5, "steel": 0.5, "fairy": 0.5},
    "water":     {"electric": 2, "grass": 2, "fire": 0.5, "water": 0.5, "ice": 0.5, "steel": 0.5},
    "electric":  {"ground": 2, "electric": 0.5, "flying": 0.5, "steel": 0.5},
    "grass":     {"fire": 2, "ice": 2, "poison": 2, "flying": 2, "bug": 2, "water": 0.5, "electric": 0.5, "grass": 0.5, "ground": 0.5, "steel": 0.5},
    "ice":       {"fire": 2, "fighting": 2, "rock": 2, "steel": 2, "ice": 0.5},
    "fighting":  {"flying": 2, "psychic": 2, "fairy": 2, "bug": 0.5, "rock": 0.5, "dark": 0.5, "steel": 0.5},
    "poison":    {"ground": 2, "psychic": 2, "fighting": 0.5, "poison": 0.5, "bug": 0.5, "grass": 0.5, "fairy": 0.5},
    "ground":    {"water": 2, "ice": 2, "grass": 2, "poison": 0.5, "rock": 0.5, "electric": 0},
    "flying":    {"electric": 2, "ice": 2, "rock": 2, "fighting": 0.5, "bug": 0.5, "grass": 0.5},
    "psychic":   {"bug": 2, "ghost": 2, "dark": 2, "fighting": 0.5, "psychic": 0.5},
    "bug":       {"fire": 2, "flying": 2, "rock": 2, "fighting": 0.5, "ground": 0.5, "grass": 0.5},
    "rock":      {"water": 2, "grass": 2, "fighting": 2, "ground": 2, "steel": 2, "normal": 0.5, "fire": 0.5, "poison": 0.5, "flying": 0.5},
    "ghost":     {"ghost": 2, "dark": 2, "normal": 0, "psychic": 0.5},
    "dragon":    {"ice": 2, "dragon": 2, "fairy": 2, "fire": 0.5, "water": 0.5, "electric": 0.5, "grass": 0.5},
    "dark":      {"fighting": 2, "bug": 2, "fairy": 2, "psychic": 0, "ghost": 0.5, "dark": 0.5},
    "steel":     {"fire": 2, "fighting": 2, "ground": 2, "ice": 0.5, "normal": 0.5, "grass": 0.5, "ice": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 0.5, "dragon": 0.5, "steel": 0.5, "fairy": 0.5},
    "fairy":     {"poison": 2, "steel": 2, "fighting": 0.5, "bug": 0.5, "dark": 0.5, "dragon": 0},
}

# OFFENSE_CHART: Effektivität eigener Angriffe auf Zieltypen
OFFENSE_CHART = {
    "normal":    {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire":      {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2},
    "water":     {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
    "electric":  {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2, "dragon": 0.5},
    "grass":     {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
    "ice":       {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5},
    "fighting":  {"normal": 2, "ice": 2, "rock": 2, "dark": 2, "steel": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "fairy": 0.5, "ghost": 0},
    "poison":    {"grass": 2, "fairy": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0},
    "ground":    {"fire": 2, "electric": 2, "poison": 2, "rock": 2, "steel": 2, "grass": 0.5, "bug": 0.5, "flying": 0},
    "flying":    {"grass": 2, "fighting": 2, "bug": 2, "electric": 0.5, "rock": 0.5, "steel": 0.5},
    "psychic":   {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug":       {"grass": 2, "psychic": 2, "dark": 2, "fire": 0.5, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "ghost": 0.5, "steel": 0.5, "fairy": 0.5},
    "rock":      {"fire": 2, "ice": 2, "flying": 2, "bug": 2, "fighting": 0.5, "ground": 0.5, "steel": 0.5},
    "ghost":     {"psychic": 2, "ghost": 2, "normal": 0, "dark": 0.5},
    "dragon":    {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark":      {"psychic": 2, "ghost": 2, "fighting": 0.5, "dark": 0.5, "fairy": 0.5},
    "steel":     {"ice": 2, "rock": 2, "fairy": 2, "fire": 0.5, "water": 0.5, "electric": 0.5, "steel": 0.5},
    "fairy":     {"fighting": 2, "dragon": 2, "dark": 2, "fire": 0.5, "poison": 0.5, "steel": 0.5},
}


def calculate_weaknesses(types):
    if not types:
        return []

    effectiveness = {atk_type: 1.0 for atk_type in DEFENSE_CHART.keys()}
    for t in types:
        t = t.lower()
        if t in DEFENSE_CHART:
            for atk_type, mult in DEFENSE_CHART[t].items():
                effectiveness[atk_type] *= mult

    return sorted(
        [typ for typ, eff in effectiveness.items() if eff > 1],
        key=lambda x: effectiveness[x],
        reverse=True
    )

# Berechnung Stärken
def calculate_strengths(types):
    if not types:
        return []

    strengths = set()
    for target_type in OFFENSE_CHART.keys():
        total = 1.0
        for atk in types:
            atk = atk.lower()
            if atk in OFFENSE_CHART:
                mult = OFFENSE_CHART[atk].get(target_type, 1.0)
                total *= mult
        if total > 1:
            strengths.add(target_type)

    return sorted(strengths)

