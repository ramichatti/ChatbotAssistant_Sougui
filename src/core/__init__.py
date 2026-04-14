"""
Core modules for Sougui AI Chatbot
"""

from .config import *
from .database_handler import DatabaseHandler
from .llm_handler import LLMHandler
from .smart_assistant import SmartAssistant

__all__ = [
    'DatabaseHandler',
    'LLMHandler', 
    'SmartAssistant',
    'DB_CONFIG',
    'OLLAMA_MODEL',
    'SOUGUI_COLORS',
    'DB_SCHEMA'
]
