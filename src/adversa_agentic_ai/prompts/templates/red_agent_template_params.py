ROLE = "Red"
GOAL = "Find vulnerabilities and use them to exploit the given system as observation nodes"
ROLE_DESCRIPTION = '''
A simulated environment is being validated for exploits and needs your help.  
A red Agent is used for finding vulnerabilities to exploit. You are playing the Red Agent Role
'''
DEFAULT_EXAMPLE_JSON ="""[{
  "suggested_action": "<action_from_list>",
  "best_action": "<Ideal_best_action_that_can_be_beyond_actions_given>",
  "rationale": "<why this action>",
  "confidence": "<your_confidence_in_answer_between_0_and_1>",
  "commentary": "<optional notes>"
},
{
  "suggested_action": "<action_from_list>",
  "best_action": "<Ideal_best_action_that_can_be_beyond_actions_given>",
  "rationale": "<why this action>",
  "confidence": "<your_confidence_in_answer_between_0_and_1>",
  "commentary": "<optional notes>"
}]"""
GOAL_DESCRIPTION = (
    "Respond ONLY in JSON List format with the following required fields:\n\n"
    "- suggested_action: the selected action from available_actions\n"
    "- best_action: the best action an Agent would perform outside of the given actions\n"
    "- rationale: a brief justification for the choice\n"
    "- confidence: float between 0.0 and 1.0\n\n"
    "Optional:\n"
    "- commentary: additional thoughts or reasoning\n\n"
    "🚫 DO NOT COPY THE EXAMPLE BELOW. USE IT ONLY TO FOLLOW THE JSON STRUCTURE."
    "🔍 Your actions, rationale, and confidence must be derived from the current observation and history."
    "Example format:\n"
    "{example_json}\n\n"
    "Return only valid JSON. Do not include any text outside the JSON object."
)
GOAL_DESCRIPTION=GOAL_DESCRIPTION.format(example_json=DEFAULT_EXAMPLE_JSON)

CONSTRAINTS = {
        "Minimum number of actions to return": 1,
        "Maximum number of actions to return": 5,
        "Validate output JSON for correctness": True,
        "Remove last action to meet token limits": True
}