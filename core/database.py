# core/database.py
import sqlite3
import json

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path  # ← No connection here!

    def get_all_game_versions(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        versions = set()
        try:
            cursor.execute("SELECT raw_data FROM pokemon")
            for row in cursor.fetchall():
                try:
                    data = json.loads(row[0])
                    # Encounters: version
                    for enc in data.get("encounters", []):
                        for detail in enc.get("version_details", []):
                            v = detail.get("version")
                            if v: versions.add(v)
                except:
                    continue
        finally:
            conn.close()
        return sorted(versions) or ["platinum"]

    def get_pokemon_by_name(self, name: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT raw_data FROM pokemon WHERE name = ?", (name.lower(),))
            row = cursor.fetchone()
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
            print(f"DB error for {name}: {e}")
            return None
        finally:
            conn.close()

    def get_moves_for_pokemon(self, name: str, version: str, level: int):
        # Normalize the target version
        search_version = version.lower().replace(" ", "-")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT raw_data FROM pokemon WHERE name = ?", (name.lower(),))
            row = cursor.fetchone()
            if not row:
                print(f"⚠️ Pokémon {name} not found!")
                return []

            data = json.loads(row[0])
            valid_moves = []

            for move_entry in data.get("moves", []):
                move_name = move_entry.get("name", "unknown")
                for method in move_entry.get("learn_methods", []):
                    method_type = method.get("method")
                    method_level = method.get("level", 999)
                    version_group = method.get("version_group", "")

                    # Only level-up moves (you can extend this!)
                    if method_type != "level-up":
                        continue
                    if method_level > level:
                        continue

                    # Check if the version is contained in version_group (case-insensitive)
                    if search_version in version_group.lower():
                        valid_moves.append(move_name)
                        break  # Only once per move

            #print(f"✅ Found moves for {name} (Version: {version}, Level: {level}): {valid_moves}")
            return valid_moves

        except Exception as e:
            print(f"❌ Move error for {name}: {e}")
            return []
        finally:
            conn.close()

    def get_encounters_for_version(self, pokemon_name: str, version: str):
        search_version = version.lower()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT raw_data FROM pokemon WHERE name = ?", (pokemon_name.lower(),))
            row = cursor.fetchone()
            if not row:
                return []

            data = json.loads(row[0])
            locations = []

            for encounter in data.get("encounters", []):
                location_name = encounter.get("location", "Unknown location")
                for detail in encounter.get("version_details", []):
                    if detail.get("version", "").lower() == search_version:
                        locations.append(location_name)
                        break

            return list(dict.fromkeys(locations))  # Preserve order

        except Exception as e:
            print(f"Error loading encounters for {pokemon_name} ({version}): {e}")
            return []
        finally:
            conn.close()


class PokemonData:
    def __init__(self, name, types, image_path, locations):
        self.name = name
        self.types = types
        self.image_path = image_path
        self.locations = locations