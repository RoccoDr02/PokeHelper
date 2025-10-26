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

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "types": self.types,
            "moves": self.moves,
            "image_path": self.image_path,
            "locations": self.locations,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "level_up_moves": self.level_up_moves
        }