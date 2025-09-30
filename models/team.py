# models/team.py
class Team:
    def __init__(self, name: str, game_version: str = "platinum", pokemon=None):
        self.name = name
        self.game_version = game_version
        self.pokemon = pokemon or []  # Liste von Pokemon-Objekten

    def add_pokemon(self, pokemon):
        if len(self.pokemon) < 6:
            self.pokemon.append(pokemon)

    def save_to_db(self, db):
        db.save_team(self)

    @classmethod
    def load_from_db(cls, db, team_id):
        return db.load_team(team_id)

    @classmethod
    def from_dict_list(cls, data_list, name: str = "Unbenanntes Team", game_version: str = "platinum"):
        """Erstellt ein Team aus einer Liste von Pokémon-Dictionaries"""
        pokemon_objects = []
        for d in data_list:
            if d:
                pokemon_objects.append(Pokemon.from_dict(d))
        return cls(name=name, game_version=game_version, pokemon=pokemon_objects)

    def to_dict(self):
        """Exportiert das Team als Dict für JSON-Speicherung"""
        return {
            "name": self.name,
            "game_version": self.game_version,
            "pokemon": [p.to_dict() for p in self.pokemon]
        }


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
