from ..schemas.agents import Agent

class AgentStore:
    def __init__(self):
        self.db = {}

    def save(self, agent: Agent) -> Agent:
        self.db[agent.id] = agent
        return agent

    def get(self, agent_id: str) -> Agent | None:
        return self.db.get(agent_id)

    def update(self, agent_id: str, agent: Agent) -> Agent:
        self.db[agent_id] = agent
        return agent

    def delete(self, agent_id: str):
        self.db.pop(agent_id, None)

    def list_all(self) -> list[Agent]:
        return list(self.db.values())
