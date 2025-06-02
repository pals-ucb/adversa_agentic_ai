import argparse
import requests
from typing import List
from pydantic import BaseModel


# Reuse Prompt classes (must match what's in your base_llm_agent.py)

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
    parser = argparse.ArgumentParser(description="Red Agent Test Driver")
    parser.add_argument("--os-version", default="20.04", help="Operating system version")
    parser.add_argument("--apache-version", default="2.4.41", help="Apache server version")
    parser.add_argument("--custom-prompt", help="Custom prompt to override default prompt generation")
    parser.add_argument("--agent-url", default="http://localhost:8000/agent/act", help="Agent /act endpoint")

    args = parser.parse_args()

    # Build observation
    if args.custom_prompt:
        observation = {"custom_prompt": args.custom_prompt}
    else:
        prompt_input = build_prompt_input(args.os_version, args.apache_version)
        observation = prompt_input.model_dump()

    # Send request to agent
    try:
        response = requests.post(args.agent_url, json=observation)
        response.raise_for_status()
        print("Agent Response:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error invoking agent: {e}")


if __name__ == "__main__":
    main()
