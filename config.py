"""Configuration management for LearnMate agent."""

import os
import streamlit as st
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env locally (ignored on Streamlit Cloud, safe to keep)
load_dotenv()


class Config(BaseModel):
    """Configuration model for LearnMate agent."""
    
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )

    class Config:
        env_prefix = ""
        case_sensitive = False


def load_config() -> Config:
    """Load and validate configuration from environment variables or Streamlit secrets."""

    openai_key = (
        os.getenv("OPENAI_API_KEY")
        or st.secrets.get("OPENAI_API_KEY", None)
    )

    if not openai_key:
        raise ValueError(
            "OpenAI API key is required. "
            "Set OPENAI_API_KEY in Streamlit Secrets or environment variables."
        )

    return Config(
        openai_api_key=openai_key
    )
