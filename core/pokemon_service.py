# core/pokemon_service.py
from models.pokemon import Pokemon
from core.database import Database
import sqlite3
import json  # ← WICHTIG: json importieren!

# ===== Typ-Effektivitäts-Tabelle =====
TYPE_CHART = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 2, "grass": 0.5, "ice": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 2},
    "water": {"fire": 0.5, "water": 0.5, "grass": 2, "ground": 2, "rock": 0.5, "dragon": 0.5},
    "electric": {"water": 0.5, "electric": 0.5, "grass": 2, "ground": 0, "flying": 0.5, "dragon": 0.5},
    "grass": {"fire": 2, "water": 0.5, "grass": 0.5, "poison": 2, "ground": 0.5, "flying": 2, "bug": 2, "rock": 2, "dragon": 0.5, "steel": 0.5},
    "ice": {"fire": 2, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 2},
    "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "fairy": 0.5},
    "poison": {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2},
    "ground": {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
    "flying": {"electric": 0.5, "grass": 2, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug": {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5},
    "ghost": {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
    "dragon": {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark": {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "steel": 0.5, "fairy": 2},
    "fairy": {"fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2, "dark": 2, "steel": 0.5},
}

def _calculate_weaknesses(types):
    if not types:
        return []
    effectiveness = {t: 1.0 for t in TYPE_CHART}
    for t in types:
        t = t.lower()
        if t in TYPE_CHART:
            for atk_type, mult in TYPE_CHART[t].items():
                effectiveness[atk_type] *= mult
    return sorted([typ for typ, eff in effectiveness.items() if eff > 1], key=lambda x: effectiveness[x], reverse=True)

def _calculate_strengths(types):
    if not types:
        return []
    strengths = set()
    all_types = list(TYPE_CHART.keys())
    for target in all_types:
        total = 1.0
        for our_type in types:
            our_type = our_type.lower()
            if our_type in TYPE_CHART and target in TYPE_CHART[our_type]:
                total *= TYPE_CHART[our_type][target]
        if total > 1:
            strengths.add(target)
    return sorted(strengths)


class PokemonService:
    def __init__(self, db: Database):
        self.db = db  # ← Speichert die Database-Instanz

    def fetch_pokemon(self, name, level, game_version):
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT raw_data FROM pokemon WHERE name = ?", (name.lower(),))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Pokémon '{name}' nicht gefunden.")

        data = json.loads(row[0])
        types = data.get("types", [])
        strengths = _calculate_strengths(types)
        weaknesses = _calculate_weaknesses(types)

        # 🔥 Korrekte Move-Logik mit Level + Version
        moves = []
        for move_entry in data.get("moves", []):
            move_name = move_entry.get("name")
            if not move_name:
                continue
            for method in move_entry.get("learn_methods", []):
                # Nur Level-Up-Moves berücksichtigen (optional: du kannst "machine" etc. später hinzufügen)
                if method.get("method") != "level-up":
                    continue

                move_level = method.get("level", 999)
                if move_level > level:
                    continue  # Noch nicht gelernt

                version_group = method.get("version_group", "")
                # ✅ Prüfe: Ist game_version Teil der version_group?
                if game_version in version_group:
                    moves.append(move_name)
                    break  # Nur einmal pro Move

        # Optional: Max. 4 Moves (wie im echten Spiel)
        moves = moves[:4]

        # Fundorte (wie vorher)
        locations = []
        for encounter in data.get("encounters", []):
            for detail in encounter.get("version_details", []):
                if detail.get("version") == game_version:
                    locations.append(encounter.get("location", "Unbekannt"))
                    break

        return Pokemon(
            name=data["name"],
            level=level,
            types=types,
            moves=moves,
            image_path=data.get("image_path"),
            strengths=strengths,
            weaknesses=weaknesses,
            locations=locations
        )