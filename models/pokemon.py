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