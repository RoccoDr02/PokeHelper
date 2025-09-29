# core/database.py
import sqlite3
import json

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path  # ← Keine Verbindung hier!

    def get_all_game_versions(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        versions = set()
        try:
            cursor.execute("SELECT raw_data FROM pokemon")
            for row in cursor.fetchall():
                try:
                    data = json.loads(row[0])
                    """# Moves: version_group
                    for move in data.get("moves", []):
                        for method in move.get("learn_methods", []):
                            v = method.get("version_group")
                            if v: versions.add(v)"""
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
            print(f"DB-Fehler bei {name}: {e}")
            return None
        finally:
            conn.close()

    def get_moves_for_pokemon(self, name: str, version: str, level: int):
        # Normalisiere die gesuchte Version
        search_version = version.lower().replace(" ", "-")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT raw_data FROM pokemon WHERE name = ?", (name.lower(),))
            row = cursor.fetchone()
            if not row:
                print(f"⚠️ Pokémon {name} nicht gefunden!")
                return []

            data = json.loads(row[0])
            valid_moves = []

            for move_entry in data.get("moves", []):
                move_name = move_entry.get("name", "unknown")
                for method in move_entry.get("learn_methods", []):
                    method_type = method.get("method")
                    method_level = method.get("level", 999)
                    version_group = method.get("version_group", "")

                    # Nur Level-Up-Moves (du kannst das erweitern!)
                    if method_type != "level-up":
                        continue
                    if method_level > level:
                        continue

                    # Prüfe, ob die Version im version_group enthalten ist (case-insensitive)
                    if search_version in version_group.lower():
                        valid_moves.append(move_name)
                        break  # Nur einmal pro Move

            print(f"✅ Gefundene Moves für {name} (Version: {version}, Level: {level}): {valid_moves}")
            return valid_moves

        except Exception as e:
            print(f"❌ Move-Fehler bei {name}: {e}")
            return []
        finally:
            conn.close()

    def get_encounters_for_version(self, pokemon_name: str, version: str):
        """
        Gibt eine Liste von Orten zurück, an denen das Pokémon in der angegebenen Version vorkommt.
        Beispiel: ["Kraftwerk", "Route 2"]
        """
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
                location_name = encounter.get("location", "Unbekannter Ort")
                version_details = encounter.get("version_details", [])

                # Prüfe, ob die gewünschte Version in version_details enthalten ist
                for detail in version_details:
                    if detail.get("version") == version:
                        locations.append(location_name)
                        break  # Ort nur einmal hinzufügen, auch wenn mehrere Methoden existieren

            return list(set(locations))  # Entferne Duplikate

        except Exception as e:
            print(f"Fehler beim Laden der Encounters für {pokemon_name} ({version}): {e}")
            return []
        finally:
            conn.close()

class PokemonData:
    def __init__(self, name, types, image_path, locations):
        self.name = name
        self.types = types
        self.image_path = image_path
        self.locations = locations