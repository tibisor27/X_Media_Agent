import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TwitterConfig:
    """Credențiale Twitter API."""
    API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    ACCESS_TOKEN_SECRET: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
    BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")


@dataclass
class AgentConfig:
    """Setări agent pentru a evita ban."""
    MIN_DELAY_BETWEEN_POSTS: int = 60 * 60  # 1 oră minim între posturi
    MAX_DELAY_BETWEEN_POSTS: int = 60 * 180  # 3 ore maxim
    MAX_POSTS_PER_DAY: int = 5
    HUMAN_HOURS_START: int = 8   # Postează doar între 8:00
    HUMAN_HOURS_END: int = 22    # și 22:00
    DATA_FOLDER: str = "data/raw_tweets"


@dataclass
class AIConfig:
    """Setări pentru AI processing."""
    API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    API_VERSION: str = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
    DEPLOYMENT_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    IMAGE_ENHANCE_SCALE: int = 2

    WAVESPEED_API_KEY: str = os.getenv("WAVESPEED_API_KEY", "")
    ENHANCE_TIMEOUT: int = 120


# Instanțe globale
twitter_config = TwitterConfig()
agent_config = AgentConfig()
ai_config = AIConfig()