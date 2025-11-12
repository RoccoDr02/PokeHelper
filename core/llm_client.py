# core/llm_client.py
from openai import OpenAI
import anthropic
import os
from dotenv import load_dotenv, set_key
try:
    from groq import Groq
except ImportError:
    Groq = None

ENV_PATH = ".env"

if not os.path.exists(ENV_PATH):
    with open(ENV_PATH, "w") as f:
        f.write("# API Keys\n")

load_dotenv(ENV_PATH)


class LLMClient:
    def __init__(self, provider: str = "openai", model: str = None):
        self.provider = provider.lower()
        self.model = model
        self.enabled = True
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """
        Initializes the client depending on the provider, if API key is present.
        """
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_KEY")
            if not api_key:
                print("⚠️ Note: No OPENAI_KEY found – LLM currently disabled.")
                self.enabled = False
                return
            self.client = OpenAI(api_key=api_key)
            self.model = self.model or "gpt-4o-mini"

        elif self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_KEY")
            if not api_key:
                print("⚠️ Note: No ANTHROPIC_KEY found – LLM currently disabled.")
                self.enabled = False
                return
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = self.model or "claude-3-5-sonnet"

        elif self.provider == "groq":
            if Groq is None:
                print("⚠️ Note: The 'groq' package is not installed – LLM disabled.")
                self.enabled = False
                return
            api_key = os.getenv("GROQ_KEY")
            if not api_key:
                print("⚠️ Note: No GROQ_KEY found – LLM currently disabled.")
                self.enabled = False
                return
            self.client = Groq(api_key=api_key)
            self.model = self.model or "llama3-70b-8192"

        else:
            print(f"⚠️ Unknown LLM provider: {self.provider} – Client disabled.")
            self.enabled = False

    def chat(self, messages: list[dict]) -> str:
        if not self.enabled or self.client is None:
            return "⚠️ No active LLM available – please enter API key."

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
        Sets the API key for a provider, saves it to .env,
        updates the environment, and reinitializes the client.
        """
        key_name = {
            "openai": "OPENAI_KEY",
            "anthropic": "ANTHROPIC_KEY",
            "groq": "GROQ_KEY"
        }.get(provider.lower())

        if not key_name:
            print(f"⚠️ Unknown provider: {provider}")
            return

        set_key(ENV_PATH, key_name, key)
        os.environ[key_name] = key
        print(f"✅ API key for {provider} saved.")

        if provider.lower() == self.provider:
            print("🔄 Reinitializing LLM client...")
            self.enabled = True
            self._initialize_client()