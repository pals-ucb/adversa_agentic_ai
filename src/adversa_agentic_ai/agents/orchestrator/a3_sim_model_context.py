import json
import uuid
from typing import Dict, List, Any

from pydantic import BaseModel
from adversa_agentic_ai.utils.config_logger import get_agent_logger
from agentic_cbsim.cyberbattle._env.cyberbattle_env import CyberBattleEnv 
from adversa_agentic_ai.models.model_convertor import ConvertedSimModel
from adversa_agentic_ai.api.schemas.sim import SimStatus, Observation
from adversa_agentic_ai.api.schemas.sim_models import NodeType
from adversa_agentic_ai.mcp.mcp_message import MCPMessage
from adversa_agentic_ai.prompts.templates.default_template import DEFAULT_PROMPT_TEMPLATE
from adversa_agentic_ai.prompts.templates import red_agent_template_params as red_params
from adversa_agentic_ai.prompts.templates import blue_agent_template_params as blue_params
from adversa_agentic_ai.agents.actions.base_actions import BaseActions
from adversa_agentic_ai.agents.actions.red_agent_actions import RedAgentActions
from adversa_agentic_ai.agents.actions.blue_agent_actions import BlueAgentActions


logger = get_agent_logger()

class AgentContext(BaseModel):
    agent_id: str = ""
    history: List[Dict[str,Any]] = []
    total_reward: int = 0

class SimModelContext:
    def __init__(self, model_id: str, a3_model: Dict[str, Any]):
        self.model_id = model_id
        self.a3_model = a3_model
        self.sim_id: uuid.uuid4 = None
        self.cbsim_model: Any = None
        self.cbsim: Any = None
        self.status: SimStatus = SimStatus.Unloaded
        self.step: int = 0
        self.epoch: int = 0
        self.total_reward = 0
        self.cbsim_obs: Any = None
        self.observations: Any = None
        #self.history: Dict[str, List[Dict[str, Any]]] = {}
        self.agent_context: Dict[str, AgentContext] = {}
        self.current_node_id = None
        logger.info(f"SimContex: a3_model: {self.a3_model}")

    def init_cbsim_model(self) -> bool:
        try:
            self.cbsim_model = ConvertedSimModel(self.a3_model)
            self.status = SimStatus.Loaded
            return True
        except Exception as e:
            logger.exception(f"Conversion to CBSim failed: {e}")
            return False

    def reset(self):
        self.step = 0
        self.epoch = 0
        self.total_reward = 0
        self.init_cbsim_model()
        self.observations = {}
        self.history.clear()

    def get_attacker_actions(self):
        if hasattr(self.cbsim, "action_space"):
            action_space = self.cbsim.action_space
            if hasattr(action_space, "sample"):
                # Get 10 sample actions as a placeholder
                return [action_space.sample() for _ in range(10)]
            else:
                logger.warning("action_space does not support 'sample'")
                return []
        else:
            logger.warning("cbsim has no action_space attribute")
            return []

        return available_actions
    
    def get_defender_actions(self):
        return ["Alarm"]
    
    def set_current_step_node_id(self):
        asset_nodes = self.get_nodes_by_type(NodeType.Asset)
        try:
            self.current_node_id = asset_nodes[self.step % len(asset_nodes)]
        except:
            raise ValueError(f"current step: {self.step} node not present")
        logger.info(f"selecting node with node_id: {self.current_node_id}")

    def get_current_observations(self):
        if not self.current_node_id:
            raise ValueError(f"Invalid current node id")
        return self.get_observation_for_node(self.current_node_id)

    def get_current_reward(self):
        if not self.current_node_id:
            raise ValueError(f"Invalid current node id")
        for node in self.a3_model.nodes:
            if node.id == self.current_node_id:
                return node.reward_score
        raise ValueError(f"Invalid current node_id")

    def get_node_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract the current state of all nodes in the simulation.
        Useful for internal inspection or debugging.
        """
        node_states = {}
        for node_name, node in self.cbsim.environment.network.nodes.items():
            node_states[node_name] = {
                "OS": node.get("os"),
                "Services": node.get("services", []),
                "Vulnerabilities": [v["name"] for v in node.get("vulnerabilities", [])],
                "Is Active": node.get("agent_installed", False),
                "Is Privileged": node.get("agent_is_privileged", False),
                "Credential Store": [str(c) for c in node.get("credentials", [])],
            }
        return node_states
    
    def summarize_node_states(self) -> str:
        states = self.get_node_states()
        lines = []
        for name, info in states.items():
            lines.append(f"- Node: {name}, OS: {info['OS']}, Active: {info['Is Active']}, Privileged: {info['Is Privileged']}")
        return "\n".join(lines)

    def do_step(self):
        action = self.cbsim.sample_valid_action()
        self.cbsim_obs, reward, done, _, self.cbsim_info = self.cbsim.step(action)
        #print(f"Step {self.step}: Action: {action}, Reward: {reward} obs: {self.cbsim_obs}")
        self.total_reward += reward
        self.step += 1

    def update_observation(self, obs: Dict[str, Any]):
        self.observations = obs

    def record_history(self, role: str, entry: Dict[str, Any]):
        self.history.setdefault(role, []).append(entry)

    def get_history(self, role: str) -> List[Dict[str, Any]]:
        return self.history.get(role, [])

    def advance_step(self):
        self.step += 1

    def is_ready(self):
        return self.status in {SimStatus.Loaded, SimStatus.Paused}

    def mark_running(self):
        self.status = SimStatus.Running

    def mark_completed(self):
        self.status = SimStatus.Completed

    def mark_error(self):
        self.status = SimStatus.Error

    def build_red_agent_MCPMessage(self) -> MCPMessage :
        message = MCPMessage(
            role=red_params.ROLE,
            goal=red_params.GOAL,
            role_description=red_params.ROLE_DESCRIPTION,
            goal_description=red_params.GOAL_DESCRIPTION,
            event_count=self.step,
            observation=self.get_current_observations(),
            prompt_template=DEFAULT_PROMPT_TEMPLATE,
            available_actions = sorted(
                set(
                    [e.value for e in BaseActions] +
                    [e.value for e in RedAgentActions] 
                )
            ),
            constraints=red_params.CONSTRAINTS,
            available_tools=[],
            history=[]
        )
        return message
    
    def build_blue_agent_MCPMessage(self) -> MCPMessage :
        message = MCPMessage(
            role=blue_params.ROLE,
            goal=blue_params.GOAL,
            role_description=blue_params.ROLE_DESCRIPTION,
            goal_description=blue_params.GOAL_DESCRIPTION,
            event_count=self.step,
            observation=self.get_current_observations(),
            prompt_template=DEFAULT_PROMPT_TEMPLATE,
            available_actions = sorted(
                set(
                    [e.value for e in BaseActions] +
                    [e.value for e in BlueAgentActions] 
                )
            ),
            constraints=blue_params.CONSTRAINTS,
            available_tools=[],
            history=[]
        )
        return message

    def get_nodes_by_type(self, node_type: str) -> list[str]:
        """
        Return all node IDs that match the given node_type from self.sim_model.

        Args:
            node_type (str): The node_type to filter by, e.g., "Person" or "Asset".

        Returns:
            List of node IDs matching the given type.
        """
        return [
            node.id
            for node in self.a3_model.nodes
            if getattr(node, "node_type", None) == node_type
        ]


    def get_observation_for_node(self, node_id: str) -> Observation:
        """
        Build a detailed Observation object for a given node_id.

        Args:
            node_id (str): The node ID to extract an observation for.

        Returns:
            Observation: The Observation Pydantic model populated with node data.
        """
        for node in self.a3_model.nodes:
            if node.id == node_id:
                return Observation(
                    id=node.id,
                    name=node.name,
                    node_type=getattr(node, "node_type", "Unknown"),
                    properties={prop.key: prop.value for prop in node.properties},
                    vulnerabilities=[
                        {
                            "id": v.id,
                            "type": v.type,
                            "subtype": v.subtype,
                            "description": v.description,
                            "vclass": v.vclass,
                            "outcome": v.outcome,
                            "outcome_type": v.outcome_type,
                            "outcome_params": v.outcome_params,
                        }
                        for v in getattr(node, "vulnerabilities", [])
                    ],
                    reachable_nodes=getattr(node, "reachable_nodes", []),
                    credentials=[cred.id for cred in getattr(node, "credentials", [])]
                )
        raise ValueError(f"Node '{node_id}' not found in model.")

    def get_observation_for_node(self, node_id: str) -> dict:
        """
        Build a detailed observation dictionary for a given node_id.

        Args:
            node_id (str): The node ID to extract an observation for.

        Returns:
            dict: Observation including all properties, services, vulnerabilities, reachable nodes, and credentials.
        """
        for node in self.a3_model.nodes:
            if node.id == node_id:
                return {
                    "id": node.id,
                    "name": node.name,
                    "node_type": getattr(node, "node_type", "Unknown"),
                    "properties": {prop.key: prop.value for prop in node.properties},
                    "services": [s.name for s in getattr(node, "services", [])],
                    "vulnerabilities": [
                        {
                            "id": v.id,
                            "type": v.type,
                            "subtype": v.subtype,
                            "description": v.description,
                            "vclass": v.vclass,
                            "outcome": v.outcome,
                            "outcome_type": v.outcome_type,
                            "outcome_params": v.outcome_params,
                        }
                        for v in getattr(node, "vulnerabilities", [])
                    ],
                    "reachable_nodes": getattr(node, "reachable_nodes", []),
                    "credentials": [cred.id for cred in getattr(node, "credentials", [])],
                }
        raise ValueError(f"Node '{node_id}' not found in model.")
