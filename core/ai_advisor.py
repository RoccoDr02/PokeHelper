# core/ai_advisor.py
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from models.team import Team
from core.database import Database

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
        """Bisherige Funktion: Team analysieren & Verbesserungen vorschlagen"""
        pokemon_data = []
        for p in team.pokemon:
            poke_data = self.db.get_pokemon_by_name(p.name)
            types = poke_data.types if poke_data else ["Unbekannt"]

            locations = self.db.get_encounters_for_version(p.name, self.game_version)

            moves = self.db.get_moves_for_pokemon(
                name=p.name,
                version=self.game_version,
                level=p.level
            )

            pokemon_data.append({
                "name": p.name,
                "types": types,
                "locations_in_version": locations,
                "moves": moves,
                "level": p.level
            })

        team_data = {
            "game_version": self.game_version,
            "pokemon": pokemon_data
        }

        prompt = f"""
        Du bist Professor Eich und hilfst in Pokémon {self.game_version}.
        Moves und Locations nur basierend auf version beantworten.

        Team des Trainers:
        {json.dumps(team_data, indent=2, ensure_ascii=False)}

        Antworte präzise, hilfreich und im Stil von Professor Eich.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def ask_question(self, team: Team, question: str) -> str:
        """Neue Funktion: beliebige Frage stellen mit Team-Kontext"""
        team_data = []
        for p in team.pokemon:
            if p:
                team_data.append({
                    "name": p.name,
                    "level": p.level,
                    "types": getattr(p, "types", []),
                    "moves": getattr(p, "moves", [])
                })

        prompt = f"""
        Du bist Professor Eich und hilfst in Pokémon {self.game_version}.
        Beziehe dich NUR auf diese Version – keine anderen Versionen!

        Aktuelles Team des Trainers:
        {json.dumps(team_data, indent=2, ensure_ascii=False)}

        Frage des Trainers:
        {question}

        Antworte präzise, hilfreich und im Stil von Professor Eich.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
