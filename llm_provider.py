import os
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()

# ── OmniRoute local gateway (352 providers, 1200+ models, runs on localhost:20128) ───
OMNIROUTE_BASE_URL = "http://localhost:20128/v1"

# ── AgentRouter (OpenAI-compatible gateway: GPT-4, Claude, etc.) ─────────────
AGENTROUTER_API_KEY = os.getenv("AGENTROUTER_API_KEY")
AGENTROUTER_BASE_URL = "https://agentrouter.org/v1"

# ── OpenRouter ────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# AgentRouter model aliases
AGENTROUTER_MODELS = {
    "gpt-4o":           "gpt-4o",
    "gpt-4o-mini":      "gpt-4o-mini",
    "claude-3-5-sonnet":"claude-3-5-sonnet-20241022",
    "claude-3-haiku":   "claude-3-haiku-20240307",
    "claude-sonnet-4":  "claude-sonnet-4-5",
    "deepseek":         "deepseek-v4-flash",
    "glm-5.3":          "glm-5.3",
    "gpt-5.6":          "gpt-5.6",
    "claude":           "claude-3-5-sonnet-20241022",
}

# OpenRouter free model aliases
OPENROUTER_FREE_MODELS = {
    "openrouter-nvidia":    "nvidia/nemotron-3.5-lightning:free",
    "openrouter-fin":       "inclusionai/ling-3.0-flash-fin:free",
    "openrouter-sante":     "inclusionai/ling-3.0-flash-sante:free",
    "openrouter-lfm":       "liquid/lfm-2.5-2.6b:free",
}


class LLMProvider:
    @staticmethod
    def get_llm(provider_name: str = "auto") -> BaseChatModel:
        provider = provider_name.lower().strip()

        # Local Ollama
        if provider == "ollama":
            print("Using Local Ollama (llama3.1)...")
            from langchain_ollama import ChatOllama
            return ChatOllama(model="llama3.1", temperature=0.7)

        # Groq
        elif provider == "groq":
            print("Using Groq (Llama 3.1 70B)...")
            return LLMProvider._get_groq()

        # OpenRouter general
        elif provider == "openrouter":
            print("Using OpenRouter (free best-effort)...")
            return LLMProvider._get_openrouter()

        # OpenRouter named aliases
        elif provider in OPENROUTER_FREE_MODELS:
            model_id = OPENROUTER_FREE_MODELS[provider]
            print(f"Using OpenRouter: {model_id}")
            return LLMProvider._get_openrouter(model_id)

        # OmniRoute local gateway — OpenAI-compatible, 352 providers, zero key needed
        elif provider == "omniroute":
            print("Using OmniRoute local gateway (localhost:20128)...")
            return LLMProvider._get_omniroute()

        elif provider.startswith("omniroute:"):
            model_id = provider.split(":", 1)[1]
            return LLMProvider._get_omniroute(model_id)

        # AgentRouter named aliases (GPT, Claude)
        elif provider in AGENTROUTER_MODELS:
            model_id = AGENTROUTER_MODELS[provider]
            print(f"Using AgentRouter: {model_id}")
            return LLMProvider._get_agentrouter(model_id)

        # AgentRouter passthrough: "agentrouter:gpt-4o"
        elif provider.startswith("agentrouter:"):
            model_id = provider.split(":", 1)[1]
            print(f"Using AgentRouter (passthrough): {model_id}")
            return LLMProvider._get_agentrouter(model_id)

        # Gemini specific model (e.g. "gemini-2.5-flash")
        elif provider.startswith("gemini-") or provider.startswith("gemini-3"):
            print(f"Using Gemini: {provider}")
            return LLMProvider._get_gemini(model=provider)

        # Gemini generic
        elif provider == "gemini" or provider == "gemini-3.1-pro":
            print("Using Gemini (default)...")
            return LLMProvider._get_gemini()

        # Auto: full fallback chain
        elif provider == "auto":
            print("Using Auto Mode (Gemini -> Groq -> OpenRouter)...")
            return LLMProvider._build_auto_chain()

        # Dynamic Ollama model
        else:
            print(f"Using Ollama dynamic model: {provider}")
            from langchain_ollama import ChatOllama
            return ChatOllama(model=provider, temperature=0.7)

    # ── Private builders ──────────────────────────────────────────────────────

    @staticmethod
    def _get_gemini(model: str = None) -> BaseChatModel:
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not model:
            # Updating to latest available supported model version
            model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0.7,
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_retries=1,
            timeout=120,  # gRPC deadline; big synthesis prompts (>30k chars) can exceed 20s -> 504
        )

    @staticmethod
    def _get_groq() -> BaseChatModel:
        from langchain_groq import ChatGroq
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not set")
        return ChatGroq(
            # llama-3.3-70b-versatile was decommissioned by Groq (404); gpt-oss-120b
            # confirmed live via GET /openai/v1/models. Override with GROQ_MODEL env.
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            temperature=0.7,
            max_tokens=4096,
            api_key=key,
            max_retries=1,
            timeout=60,
        )

    @staticmethod
    def _get_openrouter(model: str = "liquid/lfm-2.5-2.6b:free") -> BaseChatModel:
        from langchain_openai import ChatOpenAI
        key = os.getenv("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
        if not key:
            raise ValueError("OPENROUTER_API_KEY not set")
        return ChatOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=key,
            model=model,
            temperature=0.7,
            max_retries=1,
            timeout=20,
            default_headers={
                "HTTP-Referer": "https://astrology-ai.app",
                "X-Title": "Astrology AI"
            }
        )

    @staticmethod
    def _get_omniroute(model: str = "auto") -> BaseChatModel:
        """OmniRoute local gateway — OpenAI-compatible, 352 providers, no key needed when local."""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            base_url=OMNIROUTE_BASE_URL,
            api_key="omniroute",  # OmniRoute local doesn't need a real key
            model=model,
            temperature=0.7,
            max_retries=1,
            timeout=20,
        )

    @staticmethod
    def _get_agentrouter(model: str = "gpt-4o-mini") -> BaseChatModel:
        """AgentRouter is OpenAI-compatible — gateway to GPT-4, Claude, etc."""
        from langchain_openai import ChatOpenAI
        key = os.getenv("AGENTROUTER_API_KEY", AGENTROUTER_API_KEY)
        if not key:
            raise ValueError("AGENTROUTER_API_KEY not set")
        return ChatOpenAI(
            base_url=AGENTROUTER_BASE_URL,
            api_key=key,
            model=model,
            temperature=0.7,
            max_retries=1,
            timeout=20,
            default_headers={
                "User-Agent": "Cline/1.0.0",
                "X-Requested-With": "XMLHttpRequest"
            }
        )

    @staticmethod
    def _build_auto_chain() -> BaseChatModel:
        """Fast, bounded fallback: Gemini Flash -> Groq -> OpenRouter."""
        fallbacks = []

        # Primary: Gemini
        try:
            primary = LLMProvider._get_gemini()
        except Exception:
            try:
                primary = LLMProvider._get_groq()
            except Exception:
                primary = LLMProvider._get_openrouter()

        # Fallback 1: Groq
        try:
            fallbacks.append(LLMProvider._get_groq())
        except ValueError:
            pass

        # A single final fallback prevents retry cascades from turning a failed
        # request into a minute-long wait.
        try:
            fallbacks.append(LLMProvider._get_openrouter())
        except ValueError:
            pass

        if fallbacks:
            try:
                from google.api_core.exceptions import GoogleAPIError
                return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception, GoogleAPIError))
            except ImportError:
                return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))

        return primary
