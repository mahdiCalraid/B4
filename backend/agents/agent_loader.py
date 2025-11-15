"""Agent loader for discovering and instantiating file-based agents."""

from pathlib import Path
from typing import Dict, Optional, Type
import os

from .base_agent import BaseAgent
from modules.agents.gemini_agent import GeminiAgent
from modules.agents.base_ai_agent import BaseAIAgent


class AgentLoader:
    """
    Discovers and loads agents from the agent_definitions directory.

    Each agent is a folder containing:
    - info.txt
    - prompt.txt
    - structure_output.json
    - config.py (optional)
    - special_tools.py (optional)
    """

    def __init__(
        self,
        agents_dir: Optional[Path] = None,
        default_provider: str = "gemini"
    ):
        """
        Initialize agent loader.

        Args:
            agents_dir: Path to agents directory (defaults to ./agents/agent_definitions)
            default_provider: Default AI provider to use (gemini, openai, groq, ollama)
        """
        if agents_dir is None:
            # Default to agents/agent_definitions
            backend_dir = Path(__file__).parent.parent
            agents_dir = backend_dir / "agents" / "agent_definitions"

        self.agents_dir = Path(agents_dir)
        self.default_provider = default_provider
        self._agents_cache: Dict[str, BaseAgent] = {}
        self._providers_cache: Dict[str, BaseAIAgent] = {}

    def _get_provider(self, provider_name: str = None) -> BaseAIAgent:
        """Get or create an AI provider instance."""
        provider_name = provider_name or self.default_provider
        provider_name = provider_name.lower()

        # Check cache
        if provider_name in self._providers_cache:
            return self._providers_cache[provider_name]

        # Create new provider
        if provider_name == "gemini":
            from modules.agents.gemini_agent import GeminiAgent
            provider = GeminiAgent(
                model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            )
        elif provider_name == "openai":
            from modules.agents.openai_agent import OpenAIAgent
            provider = OpenAIAgent(
                model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            )
        elif provider_name == "groq":
            from modules.agents.groq_agent import GroqAgent
            provider = GroqAgent(
                model_name=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            )
        elif provider_name == "ollama":
            from modules.agents.ollama_agent import OllamaAgent
            provider = OllamaAgent(
                model_name=os.getenv("OLLAMA_MODEL", "llama3.2")
            )
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

        # Cache and return
        self._providers_cache[provider_name] = provider
        return provider

    def discover_agents(self) -> Dict[str, Path]:
        """
        Discover all agent folders in the agents directory.

        Returns:
            Dictionary mapping agent_id to agent folder path
        """
        if not self.agents_dir.exists():
            print(f"⚠️  Agents directory not found: {self.agents_dir}")
            return {}

        agents = {}

        for item in self.agents_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it has required files
                if (item / "prompt.txt").exists():
                    agent_id = item.name
                    agents[agent_id] = item

        return agents

    def load_agent(
        self,
        agent_id: str,
        provider: Optional[str] = None
    ) -> BaseAgent:
        """
        Load a specific agent by ID.

        Args:
            agent_id: Agent identifier (folder name)
            provider: AI provider to use (gemini, openai, groq, ollama)

        Returns:
            Loaded BaseAgent instance
        """
        # Check cache
        cache_key = f"{agent_id}:{provider or self.default_provider}"
        if cache_key in self._agents_cache:
            return self._agents_cache[cache_key]

        # Discover agents
        agents = self.discover_agents()

        if agent_id not in agents:
            raise ValueError(f"Agent not found: {agent_id}")

        # Get provider
        ai_provider = self._get_provider(provider)

        # Create agent instance
        agent = BaseAgent(
            agent_id=agent_id,
            agent_path=agents[agent_id],
            ai_provider=ai_provider
        )

        # Cache and return
        self._agents_cache[cache_key] = agent
        return agent

    def load_all_agents(self) -> Dict[str, BaseAgent]:
        """
        Load all discovered agents.

        Returns:
            Dictionary mapping agent_id to BaseAgent instance
        """
        agents = {}
        discovered = self.discover_agents()

        for agent_id in discovered.keys():
            try:
                agents[agent_id] = self.load_agent(agent_id)
            except Exception as e:
                print(f"⚠️  Failed to load agent {agent_id}: {e}")

        return agents

    def get_agent_info(self, agent_id: str) -> Dict:
        """Get metadata about an agent without loading it."""
        agents = self.discover_agents()

        if agent_id not in agents:
            raise ValueError(f"Agent not found: {agent_id}")

        agent_path = agents[agent_id]

        # Read basic info
        info_path = agent_path / "info.txt"
        if info_path.exists():
            with open(info_path, 'r') as f:
                content = f.read()
        else:
            content = "No info available"

        return {
            "agent_id": agent_id,
            "path": str(agent_path),
            "info": content,
            "has_prompt": (agent_path / "prompt.txt").exists(),
            "has_schema": (agent_path / "structure_output.json").exists(),
            "has_config": (agent_path / "config.py").exists(),
            "has_tools": (agent_path / "special_tools.py").exists()
        }

    def list_agents(self) -> Dict[str, Dict]:
        """
        List all available agents with their metadata.

        Returns:
            Dictionary mapping agent_id to metadata
        """
        agents = {}
        discovered = self.discover_agents()

        for agent_id in discovered.keys():
            try:
                agents[agent_id] = self.get_agent_info(agent_id)
            except Exception as e:
                print(f"⚠️  Failed to get info for agent {agent_id}: {e}")

        return agents


# Global loader instance
_loader = None


def get_loader() -> AgentLoader:
    """Get or create the global agent loader instance."""
    global _loader
    if _loader is None:
        _loader = AgentLoader()
    return _loader
