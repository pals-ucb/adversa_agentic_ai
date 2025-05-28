import argparse
import sys
import os
import requests
import json

# -- Parse CLI options --
def parse_command_line():
    parser = argparse.ArgumentParser(description="Agentic AI Orchestrator")
    parser.add_argument("--model-name", type=str, required=True, help="Name of the model (e.g., er, finance)")
    parser.add_argument("--model-path", type=str, required=True, help="Path to the simulation model package")
    parser.add_argument("--red-endpoint", type=str, default="http://127.0.0.1/8080", help="REST endpoint of the Red Agent")
    parser.add_argument("--max-steps", type=int, default=20, help="Max simulation steps")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()

# -- Load simulation model using centralized model loader --
def load_sim_model(model_name, model_path):
    from models.model_manager import ModelLoader
    loader = ModelLoader(model_name, model_path)
    return loader.load()

# -- Red Agent Interaction Interface --
def connect_agent(endpoint):
    return endpoint  # for REST, endpoint is the connection handle

def load_history():
    return []  # stub: fetch past interactions

def refine_history(history, current_prompt):
    return history  # stub: use LLM or heuristic to reduce history

def generate_prompt(observation, history):
    return {"observation": observation, "history": history}  # simplified structure

def prompt_agent(endpoint, prompt_payload):
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(endpoint, data=json.dumps(prompt_payload), headers=headers)
        response.raise_for_status()
        return response.json().get("action")
    except Exception as e:
        print(f"[ERROR] Failed to contact Red Agent: {e}")
        return None

# -- Main simulation loop --
def run_simulation(env, red_endpoint, max_steps, verbose):
    from cyberbattle._env.cyberbattle_env import CyberBattleEnv
    sim = CyberBattleEnv(env)
    obs = sim.reset()
    total_reward = 0
    step = 0

    agent_handle = connect_agent(red_endpoint)
    history = load_history()

    while step < max_steps:
        if verbose:
            print(f"\n--- Step {step} ---")

        current_prompt = generate_prompt(obs, refine_history(history, obs))
        red_action = prompt_agent(agent_handle, current_prompt)

        if red_action is None:
            print("[ERROR] Red Agent did not return an action. Aborting.")
            break

        obs, reward, done, _ = sim.step(red_action)
        total_reward += reward

        if verbose:
            print(f"Action: {red_action}\nReward: {reward}")

        if done:
            break

        step += 1

    print(f"\nSimulation complete. Total reward: {total_reward}")

# -- Entry point --
if __name__ == "__main__":
    args = parse_command_line()
    env = load_sim_model(args.model_name, args.model_path)
    run_simulation(env, args.red_endpoint, args.max_steps, args.verbose)
