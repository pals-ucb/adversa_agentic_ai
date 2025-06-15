import agentic_cbsim.cyberbattle.simulation.model as m
from agentic_cbsim.cyberbattle._env.cyberbattle_env import CyberBattleEnv
from adversa_agentic_ai.models import SimModel, Node, Vulnerability
from adversa_agentic_ai.models.model_interface import ModelInterface
from adversa_agentic_ai.utils.config_logger import get_agent_logger

from typing import Dict, List, Any

logger = get_agent_logger()

class ConvertedSimModel(ModelInterface):
    def __init__(self, model: SimModel):
        self.name = model.name
        self.services = []
        self.vulnerabilities = {}
        self.nodes = {}
        logger.info(f"Converting Adversa model to CBSim Model: {model.name}")
        self.default_firewall = m.FirewallConfiguration(
            incoming=[
                m.FirewallRule("HTTPS", m.RulePermission.ALLOW),
                m.FirewallRule("SSH", m.RulePermission.ALLOW)
            ],
            outgoing=[
                m.FirewallRule("HTTPS", m.RulePermission.ALLOW)
            ]
        )

        # Step 1: Convert vulnerabilities
        self._vuln_library = {}
        for node in model.nodes:
            for vuln in node.vulnerabilities:
                if not vuln.outcome_type:
                    raise ValueError(f"Missing outcome_type for vulnerability {vuln.id}")
                if not vuln.outcome_params:
                    raise ValueError(f"Missing outcome_params for vulnerability {vuln.id}")
                cbsim_vuln = self._convert_vuln(vuln)
                self._vuln_library[vuln.id] = cbsim_vuln
                self.vulnerabilities[vuln.id] = cbsim_vuln

        # Step 2: Convert nodes
        for node in model.nodes:
            self.nodes[node.id] = self._convert_node(node)

        # Step 3: Build environment
        identifiers = m.infer_constants_from_nodes(self.nodes.items(), self._vuln_library)
        self.network = m.create_network(self.nodes)

        # Step 4: Build topology from children
        for parent in model.nodes:
            for child_id in parent.children:
                self.network.add_edge(parent.id, child_id)

        self.env = m.Environment(
            network=self.network,
            vulnerability_library=self._vuln_library,
            identifiers=identifiers
        )
        logger.info(f"Conversion to CBSim Model succeeded: {model.name}")


    def _convert_vuln(self, vuln: Vulnerability) -> m.VulnerabilityInfo:
        outcome_class = self._resolve_outcome_class(vuln.outcome_type)
        try:
            outcome = outcome_class(**vuln.outcome_params)
        except Exception as e:
            raise ValueError(f"Invalid outcome_params for {vuln.id}: {e}")

        return m.VulnerabilityInfo(
            description=vuln.description,
            type=m.VulnerabilityType.REMOTE,  # MVP assumption
            outcome=outcome,
            reward_string=vuln.description,
            cost=vuln.cost,
            prereq=vuln.prereq,
            granted_access=vuln.granted_access
        )

    def _convert_node(self, node: Node) -> m.NodeInfo:
        services = [m.ListeningService(self._map_service_to_port(s.name)) for s in node.services]
        firewall = self.default_firewall if node.firewalls else m.FirewallConfiguration([], [])
        vuln_map = {v.id: self._vuln_library[v.id] for v in node.vulnerabilities}
        props = [f"{p.key}:{p.version or p.value}" for p in node.properties]

        return m.NodeInfo(
            services=services,
            firewall=firewall,
            value=getattr(node, 'value', 1.0),
            properties=props,
            vulnerabilities=vuln_map,
            agent_installed=True,
            reimagable=True
        )

    def _map_service_to_port(self, service: str) -> str:
        mapping = {
            "apache": "HTTP",
            "nginx": "HTTP",
            "sshd": "SSH",
            "smtp": "SMTP",
            "sql": "SQL"
        }
        return mapping.get(service.lower(), service.upper())

    def _resolve_outcome_class(self, outcome_type: str):
        mapping = {
            "PrivilegeEscalation": m.PrivilegeEscalation,
            "LeakedCredentials": m.LeakedCredentials,
            "LeakedNodesId": m.LeakedNodesId,
            "CustomerData": m.CustomerData,
            "LateralMove": m.LateralMove,
            "ProbeSucceeded": m.ProbeSucceeded,
            "ProbeFailed": m.ProbeFailed,
            "ExploitFailed": m.ExploitFailed,
        }
        if outcome_type not in mapping:
            raise ValueError(f"Unsupported outcome_type: {outcome_type}")
        return mapping[outcome_type]

    # -- ModelInterface required methods --
    def get_env(self) -> CyberBattleEnv:
        return self.env

    def get_model(self):
        return self

    def get_services(self):
        return self.services

    def get_vulnerabilities(self):
        return list(self.vulnerabilities.values())

    def get_nodeinfo(self):
        return self.nodes

