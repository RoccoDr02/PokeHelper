# core/llm_client.py
from openai import OpenAI
import anthropic
import os
from dotenv import load_dotenv
try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()

class LLMClient:
    def __init__(self, provider: str = "openai", model: str = None):
        self.provider = provider.lower()
        self.model = model
        self.enabled = True

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_KEY")
            if not api_key:
                print("⚠️ Hinweis: Kein OPENAI_KEY gefunden – LLM derzeit deaktiviert.")
                self.enabled = False
                self.client = None
                return
            self.client = OpenAI(api_key=api_key)
            self.model = model or "gpt-4o-mini"

        elif self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_KEY")
            if not api_key:
                print("⚠️ Hinweis: Kein ANTHROPIC_KEY gefunden – LLM derzeit deaktiviert.")
                self.enabled = False
                self.client = None
                return
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model or "claude-3-5-sonnet"

        elif self.provider == "groq":
            if Groq is None:
                print("⚠️ Hinweis: Das Paket 'groq' ist nicht installiert – LLM deaktiviert.")
                self.enabled = False
                self.client = None
                return
            api_key = os.getenv("GROQ_KEY")
            if not api_key:
                print("⚠️ Hinweis: Kein GROQ_KEY gefunden – LLM derzeit deaktiviert.")
                self.enabled = False
                self.client = None
                return
            self.client = Groq(api_key=api_key)
            self.model = model or "llama3-70b-8192"

        else:
            print(f"⚠️ Unbekannter LLM-Provider: {self.provider} – Client deaktiviert.")
            self.enabled = False
            self.client = None

    def chat(self, messages: list[dict]) -> str:
        if not self.enabled:
            return "⚠️ Kein aktiver LLM verfügbar – bitte API-Key eingeben."

        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=messages
            )
            return response.content[0].text

        elif self.provider == "groq":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content

    def set_api_key(self, provider: str, key: str):
        """
        Platzhalter – später wird hier der API-Key gespeichert & aktiviert.
        """
        print("🔧 set_api_key() ist noch nicht implementiert (nur Platzhalter).")
        pass
