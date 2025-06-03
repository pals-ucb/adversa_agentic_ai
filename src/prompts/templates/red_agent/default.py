from langchain_core.prompts import PromptTemplate

DEFAULT_RED_PROMPT_TEMPLATE = PromptTemplate.from_template("""
{role_description}

You are acting as a {role}.
Goal: {goal}
Event count: {event_count}

Environment Observation:
{observation}

Recent history:
{history}

{action_description}
""")

DEFAULT_ROLE = "Red"
DEFAULT_GOAL = "Maximize the owned noded."
DEFAULT_ROLE_DESCRIPTION = "A simulated environment is being validated for exploits using your help. A red entity is used for finding vulnerabilities to exploit. A blue entity is used to find the exploits and fix them."
DEFAULT_ACTION_DESCRIPTION = "Carefully analyze the above and provide the best course of action to take."
DEFAULT_EVENT_COUNT = 1
DEFAULT_OBSERVATION = ""
