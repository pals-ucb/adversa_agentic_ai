import argparse
import requests
from typing import List
from pydantic import BaseModel
from mcp.mcp_message import MCPMessage


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


def main():
    parser = argparse.ArgumentParser(description="Red Agent Test Driver (MCP-compatible)")

    # Prompt input args
    parser.add_argument("--os-version", default="20.04", help="Operating system version")
    parser.add_argument("--apache-version", default="2.4.41", help="Apache server version")

    # Agent metadata args
    parser.add_argument("--goal", default="Find vulnerabilities in the ER system", help="Agent's goal")
    parser.add_argument("--role", default="Red", help="Agent role (e.g., Red, Blue, Analyst)")
    parser.add_argument("--role-description", default="You are a red team agent helping to discover vulnerabilities in a simulated ER system.",
                        help="Role description for the agent")
    parser.add_argument("--action-description", default="Respond with your next best red-team action.",
                        help="Description of what the agent should output")
    parser.add_argument("--prompt-template", help="Custom Jinja-style prompt template to override default")

    parser.add_argument("--agent-url", default="http://localhost:8000/agent/act", help="Agent /act endpoint")
    args = parser.parse_args()

    # Build observation using the structured model
    prompt_input = build_prompt_input(args.os_version, args.apache_version)
    observation = prompt_input.model_dump()

    # Build constraints (can be extended later)
    constraints = {
        "must_not_touch": ["emergency_dispatch_server"],
        "time_limit": "10 steps"
    }

    # Construct MCPMessage
    message = MCPMessage(
        role=args.role,
        goal=args.goal,
        event_count=1,
        role_description=args.role_description,
        action_description=args.action_description,
        prompt_template=args.prompt_template if args.prompt_template else None,
        observation=observation,
        constraints=constraints
    )

    # Send to agent
    try:
        response = requests.post(args.agent_url, json=message.model_dump())
        response.raise_for_status()
        print("Agent Response:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error invoking agent: {e}")


if __name__ == "__main__":
    main()
