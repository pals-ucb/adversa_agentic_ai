from langchain_core.prompts import PromptTemplate

FAKED_BLUE_PROMPT_TEMPLATE = PromptTemplate.from_template('''
{role_description}

You are acting as a {role}.
Goal: {goal}
Event count: {event_count}

Environment Observation:
{observation}

Recent history:
{history}

{action_description}
''')

DEFAULT_ROLE = "Teacher"
DEFAULT_GOAL = "Educate the user to protect system."
DEFAULT_ROLE_DESCRIPTION = '''
Help the user to understand the current problems present in the system and learn details of the problems
'''
DEFAULT_ACTION_DESCRIPTION = '''
What are the states of the provided nodes. How can they be protected from harmful actions of others.
Please educate the user and provide positive actions with detailed steps needed to protect the system
'''
DEFAULT_EVENT_COUNT = 1
DEFAULT_OBSERVATION = ""