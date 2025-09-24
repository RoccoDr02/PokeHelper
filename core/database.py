# core/database.py
import sqlite3

class Database:
    def __init__(self, db_path="pokedex.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Zugriff per Name

    def get_pokemon_by_name(self, name):
        cur = self.conn.execute("SELECT * FROM pokemon WHERE name = ?", (name.lower(),))
        row = cur.fetchone()
        if row:
            return Pokemon(
                name=row["name"],
                image_path=row["image_path"],
                locations=row["locations"].split(",") if row["locations"] else []
            )
        return None

    def get_moves_for_pokemon(self, pokemon_name, game_version, level):
        # Beispiel-Query (du hast das sicher schon)
        cur = self.conn.execute("""
            SELECT move_name FROM pokemon_moves
            WHERE pokemon_name = ? AND game_version = ? AND level_learned <= ?
        """, (pokemon_name, game_version, level))
        return [row[0] for row in cur.fetchall()]

    def save_team(self, team):
        # INSERT/UPDATE teams + team_pokemon
        pass

    def load_all_teams(self):
        # Für Dropdown im StartScreen
        pass