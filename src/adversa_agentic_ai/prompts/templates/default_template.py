# Structured JSON prompt template using Python .format() placeholders
DEFAULT_PROMPT_TEMPLATE = """
{{
  "role": "{role}",
  "role_description": "{role_description}",
  "goal": "{goal}",
  "goal_description": "{goal_description}",
  "event_count": {event_count},
  "observation": {observation},
  "constraints": {constraints},
  "available_actions": {available_actions},
  "history": {history}
}}
"""

