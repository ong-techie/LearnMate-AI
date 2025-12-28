"""Semantic Kernel agent setup and configuration."""

from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from config import Config


class SemanticAgent:
    """Manages Semantic Kernel instance with OpenAI configuration."""
    
    def __init__(self, config: Config):
        """Initialize Semantic Kernel with OpenAI.
        
        Args:
            config: Configuration object with OpenAI API key
        """
        self.config = config
        self.kernel = Kernel()
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI service for Semantic Kernel."""
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        
        service = OpenAIChatCompletion(
            service_id="openai_chat",
            ai_model_id="gpt-5-nano-2025-08-07",
            api_key=self.config.openai_api_key
        )
        self.kernel.add_service(service)
    
    def get_kernel(self) -> Kernel:
        """Get the configured Semantic Kernel instance.
        
        Returns:
            Configured Semantic Kernel instance
        """
        return self.kernel

