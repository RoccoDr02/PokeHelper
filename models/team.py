# models/team.py
import os
import json

class Team:
    def __init__(self, name: str, game_version: str = "platinum", pokemon=None):
        self.name = name
        self.game_version = game_version
        self.pokemon = pokemon or []  # Liste von Pokemon-Objekten

    def add_pokemon(self, pokemon):
        if len(self.pokemon) < 6:
            self.pokemon.append(pokemon)

    # ===== JSON Save / Load Funktionen =====
    SAVE_FOLDER = "teams"  # Ordner für alle Teams

    def save_to_file(self, team_name: str = None):
        """Speichert das Team als JSON im teams/ Ordner."""
        if not os.path.exists(self.SAVE_FOLDER):
            os.makedirs(self.SAVE_FOLDER)

        name_to_save = team_name or self.name
        filepath = os.path.join(self.SAVE_FOLDER, f"{name_to_save}.json")

        data = self.to_dict()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern des Teams '{name_to_save}': {e}")
            return False

    @classmethod
    def load_from_file(cls, team_name: str):
        """Lädt ein Team aus dem teams/ Ordner anhand des Namens."""
        filepath = os.path.join(cls.SAVE_FOLDER, f"{team_name}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Team '{team_name}' existiert nicht.")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Erstelle Team-Objekt
        return cls.from_dict_list(
            data_list=data.get("pokemon", []),
            name=data.get("name", team_name),
            game_version=data.get("game_version", "platinum")
        )

    @classmethod
    def list_saved_teams(cls):
        """Gibt eine Liste aller gespeicherten Team-Dateien ohne .json zurück."""
        if not os.path.exists(cls.SAVE_FOLDER):
            return []
        files = [f[:-5] for f in os.listdir(cls.SAVE_FOLDER) if f.endswith(".json")]
        return sorted(files)
    # ========================================

    def to_dict(self):
        """Exportiert das Team als Dict für JSON-Speicherung"""
        return {
            "name": self.name,
            "game_version": self.game_version,
            "pokemon": [p.to_dict() for p in self.pokemon if p is not None]
        }

    @classmethod
    def from_dict_list(cls, data_list, name: str = "Unbenanntes Team", game_version: str = "platinum"):
        """Erstellt ein Team aus einer Liste von Pokémon-Dictionaries"""
        pokemon_objects = []
        for d in data_list:
            if d:
                pokemon_objects.append(Pokemon.from_dict(d))
        return cls(name=name, game_version=game_version, pokemon=pokemon_objects)


class Pokemon:
    def __init__(self, name: str, level: int = 100, types=None, moves=None,
                 image_path=None, locations=None, strengths=None, weaknesses=None):
        self.name = name.lower()
        self.level = level
        self.types = types or []
        self.moves = moves or []
        self.image_path = image_path
        self.locations = locations or []
        self.strengths = strengths or []
        self.weaknesses = weaknesses or []

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            name=d.get("name", "unbekannt"),
            level=d.get("level", 100),
            types=d.get("types", []),
            moves=d.get("moves", []),
            image_path=d.get("image_path"),
            locations=d.get("locations", []),
            strengths=d.get("strengths", []),
            weaknesses=d.get("weaknesses", []),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "types": self.types,
            "moves": self.moves,
            "image_path": self.image_path,
            "locations": self.locations,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses
        }
