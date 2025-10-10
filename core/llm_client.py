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

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_KEY")
            if not api_key:
                raise ValueError("OPENAI_KEY fehlt in .env")
            self.client = OpenAI(api_key=api_key)
            self.model = model or "gpt-4o-mini"

        elif self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_KEY fehlt in .env")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model or "claude-3-5-sonnet"

        elif self.provider == "groq":
            if Groq is None:
                raise ImportError("Das 'groq' Paket ist nicht installiert. Bitte `pip install groq` ausführen.")
            api_key = os.getenv("GROQ_KEY")
            if not api_key:
                raise ValueError("GROQ_KEY fehlt in .env")
            self.client = Groq(api_key=api_key)
            self.model = model or "llama3-70b-8192"

        else:
            raise ValueError(f"Unbekannter LLM-Provider: {self.provider}")

    def chat(self, messages: list[dict]) -> str:
        """Einheitliche Chat-Schnittstelle"""
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
