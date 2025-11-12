# models/team.py
import os
import json

class Team:
    def __init__(self, name: str, game_version: str = "platinum", pokemon=None):
        self.name = name
        self.game_version = game_version
        self.pokemon = pokemon or []  # List of Pokemon objects

    def add_pokemon(self, pokemon):
        if len(self.pokemon) < 6:
            self.pokemon.append(pokemon)

    # ===== JSON Save / Load Functions =====
    SAVE_FOLDER = "teams"  # Folder for all teams

    def save_to_file(self, team_name: str = None):
        """Saves the team as JSON in the teams/ folder."""
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
            print(f"Error saving team '{name_to_save}': {e}")
            return False

    @classmethod
    def load_from_file(cls, team_name: str):
        """Loads a team from the teams/ folder by name."""
        filepath = os.path.join(cls.SAVE_FOLDER, f"{team_name}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Team '{team_name}' does not exist.")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Create team object
        return cls.from_dict_list(
            data_list=data.get("pokemon", []),
            name=data.get("name", team_name),
            game_version=data.get("game_version", "platinum")
        )

    @classmethod
    def list_saved_teams(cls):
        """Returns a list of all saved team files without .json extension."""
        if not os.path.exists(cls.SAVE_FOLDER):
            return []
        files = [f[:-5] for f in os.listdir(cls.SAVE_FOLDER) if f.endswith(".json")]
        return sorted(files)
    # ========================================

    def to_dict(self):
        """Exports the team as a dict for JSON storage"""
        return {
            "name": self.name,
            "game_version": self.game_version,
            "pokemon": [p.to_dict() for p in self.pokemon if p is not None]
        }

    @classmethod
    def from_dict_list(cls, data_list, name: str = "Unnamed Team", game_version: str = "platinum"):
        """Creates a team from a list of Pokémon dictionaries"""
        pokemon_objects = []
        for d in data_list:
            if d:
                pokemon_objects.append(Pokemon.from_dict(d))
        return cls(name=name, game_version=game_version, pokemon=pokemon_objects)

    def auto_save(self):
        """
        Automatically saves the team without dialogs or user input.
        Returns True on success.
        """
        try:
            self.save_to_file(self.name)
            print(f"[AutoSave] Team '{self.name}' saved.")
            return True
        except Exception as e:
            print(f"[AutoSave] Error: {e}")
            return False


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
            name=d.get("name", "unknown"),
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