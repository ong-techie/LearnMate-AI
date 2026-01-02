"""Configuration management for LearnMate agent."""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class Config(BaseModel):
    """Configuration model for LearnMate agent."""
    
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    class Config:
        env_prefix = ""
        case_sensitive = False


def load_config() -> Config:
    """Load and validate configuration from environment variables."""
    openai_key = (os.getenv("OPENAI_API_KEY")
    or st.secrets.get("OPENAI_API_KEY", None))
    
    # Validate API key
    if not openai_key:
        raise ValueError(
            "OpenAI API key is required. "
            "Please set OPENAI_API_KEY in your .env file."
        )
    
    return Config(
        "openai_api_key"=openai_key
    )

