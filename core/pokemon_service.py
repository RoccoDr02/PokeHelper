# core/pokemon_service.py
from models.pokemon import Pokemon
from core.database import Database
import sqlite3
import json
from core.type_charts import calculate_strengths, calculate_weaknesses


class PokemonService:
    def __init__(self, db: Database):
        self.db = db

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

        # Stärke/Schwäche berechnen (bereits Listen)
        weaknesses = calculate_weaknesses(types)
        strengths = calculate_strengths(types)

        # Level-Up Moves für das Team (nur Moves <= aktuellem Level)
        level_up_moves = []
        for move_entry in data.get("moves", []):
            move_name = move_entry.get("name")
            if not move_name:
                continue
            for method in move_entry.get("learn_methods", []):
                if method.get("method") != "level-up":
                    continue
                version_group = method.get("version_group", "")
                if game_version in version_group:
                    move_level = method.get("level", 999)
                    level_up_moves.append({"name": move_name, "level": move_level})

        moves = [m["name"] for m in level_up_moves if m["level"] <= level][:4]

        # Fundorte
        locations = []
        for encounter in data.get("encounters", []):
            for detail in encounter.get("version_details", []):
                if detail.get("version") == game_version:
                    locations.append(encounter.get("location", "Unbekannt"))
                    break

        # Pokémon-Objekt erstellen
        pokemon = Pokemon(
            name=data["name"],
            level=level,
            types=types,
            moves=moves,
            image_path=data.get("image_path"),
            strengths=strengths,
            weaknesses=weaknesses,
            locations=locations
        )

        # Alle Level-Up Moves speichern, ungefiltert für das Detail-Popup
        pokemon.level_up_moves = level_up_moves

        return pokemon

    def get_all_pokemon_names(self):
        if not hasattr(self, '_all_pokemon_names_cache'):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT name FROM pokemon WHERE name IS NOT NULL AND name != ''")
                names = [row[0].lower() for row in cursor.fetchall() if row[0]]
                self._all_pokemon_names_cache = sorted(set(names))
            finally:
                conn.close()
        return self._all_pokemon_names_cache
