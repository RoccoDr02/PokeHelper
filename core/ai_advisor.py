# core/ai_advisor.py
from openai import OpenAI
from dotenv import load_dotenv
import os
from models.team import Team
from models.pokemon import Pokemon
from core.database import Database
import json

load_dotenv()

class AIAdvisor:
    def __init__(self, db: Database, game_version: str = None):
        self.db = db
        self.game_version = game_version
        api_key = os.getenv("OPENAI_KEY")
        if not api_key:
            raise ValueError("OpenAI API Key nicht gesetzt")

        self.client = OpenAI(api_key=api_key)

    def suggest_team_improvements(self, team: Team) -> str:
        team_data = []
        for p in team.pokemon:
            # Typen und Bild über get_pokemon_by_name (falls du sie brauchst)
            poke_data = self.db.get_pokemon_by_name(p.name)
            types = poke_data.types if poke_data else p.get("types", ["Unbekannt"])

            # ✅ Versions-spezifische Encounter-Orte
            locations = self.db.get_encounters_for_version(p.name, team.game_version)

            # Moves (du übergibst team.game_version als version_group – passt das?)
            moves = self.db.get_moves_for_pokemon(
                name=p.name,
                version_group=self.game_version,  # ⚠️ Stelle sicher: ist das wirklich ein "version_group"?
                level=p.level
            )

            team_data.append({
                "name": p.name,
                "types": types,
                "locations_in_version": locations,
                "moves": moves
            })

        prompt = f"""
        Du bist Professor Eich und hilfst in Pokémon {self.game_version}.
        Beziehe dich NUR auf diese Version - keine anderen Versionen erwähnen!
        Aktuelles Team mit versions-spezifischen Daten:
        {json.dumps(team_data, indent=2, ensure_ascii=False)}

        Gib präzise Tipps:
        - Wo kann der Spieler fehlende Pokémon in {self.game_version} fangen?
        - Welche Pokémon fehlen gegen typische Gegner in dieser Version?
        - Sollte das Moveset angepasst werden?
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content