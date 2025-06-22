ROLE = "Red"
GOAL = "Identify vulnerabilities and exploit observation nodes" 
ROLE_DESCRIPTION = "You are the Red Agent. Find and exploit vulnerabilities in a simulated environment."
DEFAULT_EXAMPLE_JSON ="""[{
  "suggested_action": "<action_from_list>",
  "best_action": "<Ideal_best_action_that_can_be_beyond_actions_given>",
  "rationale": "<why this action>",
  "confidence": "<your_confidence_in_answer_between_0_and_1>",
}]"""
GOAL_DESCRIPTION =(
    "Return only a JSON list of up to 3 items, each with:\n"
    "- suggested_action: one of the available_actions\n"
    "- best_action: the ideal action if unconstrained\n"
    "- rationale: reason for selection limited to 80 characters\n"
    "- confidence: float (0.0–1.0)\n"
    "Only return JSON. No extra text.\n"
    "🚫 DO NOT COPY THE EXAMPLE BELOW. USE IT ONLY TO FOLLOW THE JSON STRUCTURE.\n"
    "🔍 Your actions, rationale, and confidence must be derived from the current observation and history.\n"
    "Format:\n"
    "{example_json}"
)
GOAL_DESCRIPTION=GOAL_DESCRIPTION.format(example_json=DEFAULT_EXAMPLE_JSON)

CONSTRAINTS = {
     "Maximum actions return": 3
}