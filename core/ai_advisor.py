# core/ai_advisor.py
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from core.llm_client import LLMClient
from models.team import Team

class AIAdvisor:
    def __init__(self, db, game_version: str = None):
        self.db = db
        self.game_version = game_version

        all_llms = [
            LLMClient(provider="groq"),
            LLMClient(provider="openai"),
            LLMClient(provider="anthropic")
        ]

        self.llms = [llm for llm in all_llms if llm.enabled]
        if not self.llms:
            print("⚠️ No active LLMs available – please add API key in settings.")

    def _get_gym_leaders(self):
        """Loads gym leader data for the current game version."""
        if not self.game_version:
            return []

        sql = """
        SELECT a.name, a.stadt, a.typ, a.orden, a.reihenfolge, r.name AS regionen, v.name AS versionen
        FROM arenaleiter a
        JOIN regionen r ON a.region_id = r.id
        JOIN versionen v ON v.region_id = r.id
        WHERE LOWER(v.name) = ?  -- case-insensitive query
        ORDER BY a.reihenfolge;
        """

        leaders = []
        conn = None
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute(sql, (self.game_version.lower(),))
            rows = cursor.fetchall()
            for name, stadt, typ, orden, reihenfolge, regionen, versionen in rows:
                leaders.append({
                    "name": name.strip(),
                    "stadt": stadt.strip(),
                    "typ": typ.strip(),
                    "orden": orden.strip(),
                    "reihenfolge": reihenfolge,
                    "region": regionen.strip(),
                    "version": versionen.strip()
                })
        except Exception as e:
            print(f"❌ Error loading gym leaders: {e}")
        finally:
            if conn:
                conn.close()

        return leaders

    def _build_prompt(self, team, instruction: str = None, question: str = None) -> str:
        """Creates the prompt for the LLM, including team and gym leader data."""
        team_data = []
        for p in team.pokemon:
            team_data.append({
                "name": p.name.strip(),
                "level": p.level,
                "types": getattr(p, "types", []),
                "moves": getattr(p, "moves", [])
            })

        prompt = f"You are Professor Oak in Pokémon {self.game_version}.\n"
        prompt += f"Current team:\n{json.dumps(team_data, indent=2, ensure_ascii=False)}\n"

        gym_leaders = self._get_gym_leaders()
        if gym_leaders:
            prompt += f"\nGym Leaders in this version:\n{json.dumps(gym_leaders, indent=2, ensure_ascii=False)}\n"

        if instruction:
            prompt += f"\n{instruction}\n"
        if question:
            prompt += f"\nQuestion: {question}\n"

        prompt += "- Answer precisely, helpfully, and in the style of Professor Oak."
        return prompt

    def _score_response(self, text: str) -> int:
        score = len(text)
        if "?" in text or "Error" in text:
            score -= 50
        keywords = ["Type", "Moves", "Level", "Advantage"]
        for kw in keywords:
            if kw.lower() in text.lower():
                score += 10
        return score

    def _ensemble_chat(self, messages: list[dict]) -> str:
        if not self.llms:
            return "⚠️ No active LLM available – please add API key in settings."

        results = []
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(llm.chat, messages): llm for llm in self.llms}
            for future in futures:
                try:
                    text = future.result()
                    llm_name = futures[future].provider
                    score = self._score_response(text)
                    results.append((llm_name, text, score))
                except Exception as e:
                    results.append((f"{futures[future].provider} Error", str(e), -1))

        best = max(results, key=lambda x: x[2])
        return best[1]

    def suggest_team_improvements(self, team: Team) -> str:
        instruction = "Analyze the team and suggest meaningful improvements (2–3 paragraphs)."
        messages = [{"role": "user", "content": self._build_prompt(team, instruction=instruction)}]
        return self._ensemble_chat(messages)

    def ask_question(self, team: Team, question: str) -> str:
        messages = [{"role": "user", "content": self._build_prompt(team, question=question)}]
        return self._ensemble_chat(messages)