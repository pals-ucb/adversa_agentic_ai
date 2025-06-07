# agents/orchestrator/orchestrator_main.py
import argparse
import logging
from adversa_agentic_ai.models.model_manager import ModelManager
from cyberbattle._env.cyberbattle_env import CyberBattleEnv


def parse_arguments():
    parser = argparse.ArgumentParser(description="Agentic AI Orchestrator")

    # Model loading options
    parser.add_argument('--model_path', type=str,
                        default='/home/pals/Workspace/adversa_agentic_ai/models/healthcare',
                        help='Path to the folder containing the model')
    parser.add_argument('--model_file', type=str,
                        default='er_sim.py',
                        help='Python file containing the simulation model')
    parser.add_argument('--model_class', type=str,
                        default='ErSimModel',
                        help='Model class name inside the Python module')

    # Red agent options (placeholders)
    parser.add_argument('--red_agent_endpoint', type=str,
                        default='http://localhost:5001/query',
                        help='Red agent REST endpoint URL')
    parser.add_argument('--red_agent_name', type=str,
                        default='default_red_agent',
                        help='Name/alias of the red agent framework')

    # Simulation control
    parser.add_argument('--steps', type=int,
                        default=500,
                        help='Max number of simulation steps')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed step output')

    return parser.parse_args()

def main():
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Initialize model manager and load model
    model_manager = ModelManager()
    model_key = model_manager.add_model(args.model_path, args.model_file, args.model_class)
    logging.info(f"Loaded model with key: {model_key}")

    # Retrieve model environment
    env_raw = model_manager.get_env(model_key)
    '''
    
    env = CyberBattleEnv(env_raw)

    vulnerabilities = model_manager.get_vulnerabilities(model_key)
    services = model_manager.get_services(model_key)
    nodeinfo = model_manager.get_nodeinfo(model_key)

    logging.info(f"Node count: {len(nodeinfo)} | Services: {len(services)} | Vulnerabilities: {len(vulnerabilities)}")

    # Run simulation steps
    observation = env.reset()
    for step in range(args.steps):
        action = env.action_space.sample()
        observation, reward, done, _, info = env.step(action)
        logging.info(f"Step {step+1}: Action={action}, Reward={reward}, Done={done}")
        if done:
            break
    '''
    sim = CyberBattleEnv(env_raw)

    obs = sim.reset()
    done = False
    total_reward = 0
    MAX_STEPS = 200  # Stop after 200 steps
    step = 0

    while not done and step < MAX_STEPS:
        action = sim.sample_valid_action()
        obs, reward, done, _, info = sim.step(action)
        print(f"Step {step}: Action: {action}, Reward: {reward}")
        total_reward += reward
        step += 1

    print(f"\nTotal reward accumulated: {total_reward}")


if __name__ == '__main__':
    main()

