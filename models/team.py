class Team:
    def __init__(self, name: str, game_version: str = "platinum"):
        self.name = name
        self.game_version = game_version
        self.pokemon = []  # Liste von Pokemon-Objekten

    def add_pokemon(self, pokemon):
        if len(self.pokemon) < 6:
            self.pokemon.append(pokemon)

    def save_to_db(self, db):
        db.save_team(self)

    @classmethod
    def load_from_db(cls, db, team_id):
        return db.load_team(team_id)

class Pokemon:
    def __init__(self, name: str, level: int = 100, types=None, moves=None, image_path=None, locations=None):
        self.name = name.lower()
        self.level = level
        self.types = types or []
        self.moves = moves or []
        self.image_path = image_path  # Pfad aus DB
        self.locations = locations or []  # Wo zu finden (aus DB)