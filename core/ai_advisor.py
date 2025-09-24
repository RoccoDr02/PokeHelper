# core/ai_advisor.py
from openai import OpenAI

class AIAdvisor:
    def __init__(self, db: Database, openai_api_key: str):
        self.db = db
        self.client = OpenAI(api_key=openai_api_key)

    def suggest_team_improvements(self, team: Team) -> str:
        # Hole Fundorte für alle Pokémon im Team
        locations = {}
        for p in team.pokemon:
            locs = self.db.get_locations(p.name)
            locations[p.name] = locs

        prompt = f"""
        Du bist ein erfahrener Pokémon-Trainer und hilfst Spielern in {team.game_version}.
        Team: {[p.name for p in team.pokemon]}
        Fundorte: {locations}
        Gib konkrete Tipps:
        - Welche Pokémon fehlen gegen häufige Gegner?
        - Wo kann man fehlende Pokémon fangen?
        - Verbesserungsvorschläge für Movesets?
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content