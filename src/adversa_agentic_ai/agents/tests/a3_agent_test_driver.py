import argparse
from click import Abort
import requests
from typing import List, Dict, Any
from pydantic import BaseModel
from adversa_agentic_ai.mcp.mcp_message import MCPMessage
from adversa_agentic_ai.prompts.templates.default_template import DEFAULT_PROMPT_TEMPLATE
from adversa_agentic_ai.prompts.templates import red_agent_template_params as red_params
from adversa_agentic_ai.agents.actions.base_actions import BaseActions
from adversa_agentic_ai.agents.actions.red_agent_actions import RedAgentActions


# Reuse Prompt classes (used for structured observation)
class Software(BaseModel):
    name: str
    version: str

class Service(BaseModel):
    name: str
    port: int
    software: Software

class PromptInput(BaseModel):
    os_name: str
    os_version: str
    services: List[Service]
    user_role: str

def build_prompt_input(os_version: str, apache_version: str) -> PromptInput:
    return PromptInput(
        os_name="Ubuntu",
        os_version=os_version,
        user_role="patient",
        services=[
            Service(
                name="apache2",
                port=80,
                software=Software(name="apache2", version=apache_version)
            ),
            Service(
                name="ssh",
                port=22,
                software=Software(name="openssh", version="7.9")
            )
        ]
    )
def build_MCPMessage(event_count: int, observation: Dict[str, Any]) -> MCPMessage :
    message = MCPMessage(
        role=red_params.ROLE,
        goal=red_params.GOAL,
        role_description=red_params.ROLE_DESCRIPTION,
        goal_description=red_params.GOAL_DESCRIPTION,
        event_count=event_count,
        observation=observation,
        prompt_template=DEFAULT_PROMPT_TEMPLATE,
        available_actions = sorted(set([e.value for e in BaseActions] + [e.value for e in RedAgentActions])),
        constraints=red_params.CONSTRAINTS,
        available_tools=["nmap", "port_scan"],
        history=[]
    )
    return message

def main():
    parser = argparse.ArgumentParser(description="Red Agent Test Driver (MCP-compatible)")

    # Prompt input args
    parser.add_argument("--os-version", default="20.04", help="Operating system version")
    parser.add_argument("--apache-version", default="2.4.41", help="Apache server version")
    parser.add_argument("--agent-url", default="http://localhost:8001/aaa/agent/action", help="Agent /aaa/agent/action endpoint")
    parser.add_argument("--role", default="Red", help="Agent role (e.g., Red, Blue, Analyst)")
    args = parser.parse_args()

    # Build observation using the structured model
    prompt_input = build_prompt_input(args.os_version, args.apache_version)
    observation = prompt_input.model_dump()

    # Build constraints (can be extended later)
    

    message = build_MCPMessage(1, observation)

    # Send to agent
    try:
        print(f"Sending MCPMessage to Agent: {message}")
        response = requests.post(args.agent_url, json=message.model_dump())
        response.raise_for_status()
        print("Agent Response:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error invoking agent: {e}")


if __name__ == "__main__":
    main()
