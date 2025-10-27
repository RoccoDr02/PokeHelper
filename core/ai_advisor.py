# core/ai_advisor.py
import json
from concurrent.futures import ThreadPoolExecutor
from core.llm_client import LLMClient
from models.team import Team

class AIAdvisor:
    def __init__(self, db, game_version: str = None):
        self.db = db
        self.game_version = game_version
        # LLM-Clients vorbereiten
        all_llms = [
            LLMClient(provider="groq"),
            LLMClient(provider="openai"),
            LLMClient(provider="anthropic")
        ]
        # Nur aktivierte Clients behalten
        self.llms = [llm for llm in all_llms if llm.enabled]
        if not self.llms:
            print("⚠️ Keine aktiven LLMs verfügbar – bitte API-Key in den Einstellungen hinzufügen.")

    def _build_prompt(self, team: Team, instruction: str = None, question: str = None) -> str:
        team_data = []
        for p in team.pokemon:
            team_data.append({
                "name": p.name,
                "level": p.level,
                "types": getattr(p, "types", []),
                "moves": getattr(p, "moves", [])
            })

        prompt = f"Du bist Professor Eich in Pokémon {self.game_version}.\n"
        prompt += f"Aktuelles Team:\n{json.dumps(team_data, indent=2, ensure_ascii=False)}\n"

        if instruction:
            prompt += f"\n{instruction}\n"
        if question:
            prompt += f"\nFrage: {question}\n"

        prompt += "- Antworte präzise, hilfreich und im Stil von Professor Eich."
        return prompt

    def _score_response(self, text: str) -> int:
        score = len(text)
        if "?" in text or "Fehler" in text:
            score -= 50
        keywords = ["Typ", "Moves", "Level", "Vorteil"]
        for kw in keywords:
            if kw.lower() in text.lower():
                score += 10
        return score

    def _ensemble_chat(self, messages: list[dict]) -> str:
        if not self.llms:
            return "⚠️ Kein aktiver LLM verfügbar – bitte API-Key in den Einstellungen hinzufügen."

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
                    results.append((f"{futures[future].provider} Fehler", str(e), -1))

        best = max(results, key=lambda x: x[2])
        return best[1]

    def suggest_team_improvements(self, team: Team) -> str:
        instruction = "Analysiere das Team und schlage sinnvolle Verbesserungen vor (2–3 Absätze)."
        messages = [{"role": "user", "content": self._build_prompt(team, instruction=instruction)}]
        return self._ensemble_chat(messages)

    def ask_question(self, team: Team, question: str) -> str:
        messages = [{"role": "user", "content": self._build_prompt(team, question=question)}]
        return self._ensemble_chat(messages)
