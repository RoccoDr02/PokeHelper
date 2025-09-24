# core/pokemon_service.py
class PokemonService:
    def __init__(self, db: Database):
        self.db = db

    def fetch_pokemon(self, name: str, level: int, game_version: str) -> Pokemon:
        # 1. Basisdaten aus DB holen
        base = self.db.get_pokemon_by_name(name)
        if not base:
            raise ValueError("Pokémon nicht gefunden")

        # 2. Moves für diese Version & Level holen
        moves = self.db.get_moves_for_pokemon(name, game_version, level)

        # 3. Typen & Schwächen (kannst du auch cachen oder in DB speichern)
        types = self._get_types_from_db_or_api(name)

        # 4. Stärken/Schwächen berechnen (kannst du vorab in DB speichern!)
        strengths, weaknesses = self._calculate_type_relations(types)

        return Pokemon(
            name=name,
            level=level,
            types=types,
            moves=moves,
            image_path=base.image_path,
            locations=base.locations
        )