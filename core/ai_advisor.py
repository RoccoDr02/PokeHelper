# core/ai_advisor.py
from openai import OpenAI
from dotenv import load_dotenv
import os
from models.team import Team
from models.pokemon import Pokemon
from core.database import Database


load_dotenv()

class AIAdvisor:
    def __init__(self, db: Database):
        self.db = db

        api_key = os.getenv("OPENAI_KEY")
        if not api_key:
            raise ValueError("OpenAI API Key nicht gesetzt")

        self.client = OpenAI(api_key=api_key)

    def suggest_team_improvements(self, team: Team) -> str:
        team_data = []
        for p in team.pokemon:
            locs = self.db.get_locations(p.name)
            moves = self.db.get_moveset(p.name, team.game_version)
            types = self.db.get_types(p.name)

            team_data.append({
                "name": p.name,
                "locations": locs,
                "moves": moves,
                "types": types
            })

        prompt = f"""
        Du bist ein erfahrener Pokémon-Trainer names 'Professor Eich' und hilfst Spielern in {team.game_version}.
        Team info: {team_data}
        Gib konkrete Tipps:
        - Welche Pokémon fehlen gegen häufige Gegner?
        - Wo kann man fehlende Pokémon fangen?
        - Verbesserungsvorschläge für Movesets?
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content