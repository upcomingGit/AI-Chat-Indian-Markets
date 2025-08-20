"""
Agent registry to manage and route queries to specialized agents.
"""
from typing import Dict, List, Optional
from .base import Agent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}

    def register(self, name: str, agent: Agent) -> None:
        print(f"[AgentRegistry] Registering agent '{name}': {agent.__class__.__name__}")
        self._agents[name] = agent

    def get(self, name: str) -> Optional[Agent]:
        return self._agents.get(name)

    def all(self) -> List[Agent]:
        return list(self._agents.values())

    def list_agents(self) -> Dict[str, str]:
        """Return a mapping of registry name -> agent class name for available agents."""
        return {name: agent.__class__.__name__ for name, agent in self._agents.items()}

    def route_query(self, query: str):
        print(f"[AgentRegistry] Routing query: {query}")
        for name, agent in self._agents.items():
            try:
                can = agent.can_handle(query)
                print(f"[AgentRegistry] Agent '{name}' can_handle={can}")
                if can:
                    print(f"[AgentRegistry] Routed to agent '{name}'")
                    return agent.handle(query)
            except Exception as e:
                print(f"[AgentRegistry] Error while checking/handling with '{name}': {e}")
        return "No suitable agent found."


# Singleton registry instance for app-wide use
registry = AgentRegistry()
