from langchain.prompts import PromptTemplate

# Structured JSON prompt template using Python .format() placeholders
DEFAULT_PROMPT_TEMPLATE = PromptTemplate.from_template("""
{{
  "role": "{role}",
  "goal": "{goal}",
  "event_count": {event_count},
  "observation": {observation},
  "constraints": {constraints},
  "role_description": "{role_description}",
  "action_description": "Respond ONLY in JSON format with the following required fields. DO NOT include extra text outside the JSON object.\n\nRequired fields:\n- suggested_action: one of the available_actions\n- rationale: a brief justification\n- confidence: float between 0.0 and 1.0\n\nYou may optionally include a commentary field AFTER the above fields to elaborate on your decision.\nReturn only valid JSON.",
  "available_actions": {available_actions},
  "history": {history}
}}
""")

