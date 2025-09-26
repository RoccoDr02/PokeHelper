import sqlite3
import json

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_pokemon_by_name(self, name: str):
        """Holt Basisdaten eines Pokémon aus der DB."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT raw_data FROM pokemon WHERE name = ?", (name.lower(),))
            row = cursor.fetchone()
            conn.close()
            if row:
                data = json.loads(row[0])
                return PokemonData(
                    name=data["name"],
                    types=data.get("types", []),
                    image_path=data.get("image_path"),
                    locations=data.get("locations", [])
                )
            return None
        except Exception as e:
            print(f"DB-Fehler bei {name}: {e}")
            return None

    def get_moves_for_pokemon(self, name: str, version_group: str, level: int):
        """Filtert Moves nach Version und Level."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT raw_data FROM pokemon WHERE name = ?", (name.lower(),))
            row = cursor.fetchone()
            conn.close()
            if not row:
                return []

            data = json.loads(row[0])
            valid_moves = []
            for move_entry in data.get("moves", []):
                move_name = move_entry.get("name", "unknown")
                learned_in_version = False

                for method in move_entry.get("learn_methods", []):
                    if (method.get("method") == "level-up" and
                            method.get("version_group") == version_group and
                            method.get("level", 999) <= level):
                        learned_in_version = True
                        break

                if learned_in_version:
                    valid_moves.append(move_name)

            return valid_moves
        except Exception as e:
            print(f"Move-Fehler bei {name}: {e}")
            return []


class PokemonData:
    def __init__(self, name, types, image_path, locations):
        self.name = name
        self.types = types
        self.image_path = image_path
        self.locations = locations