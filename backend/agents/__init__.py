"""
Agent system for B4.

This package provides a flexible, file-based agent definition system
that integrates with the existing B4 AI infrastructure.
"""

from .base_agent import BaseAgent
from .agent_loader import AgentLoader

__all__ = ["BaseAgent", "AgentLoader"]
