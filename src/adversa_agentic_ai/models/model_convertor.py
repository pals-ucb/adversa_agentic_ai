import copy
import agentic_cbsim.cyberbattle.simulation.model as m
from agentic_cbsim.cyberbattle._env.cyberbattle_env import CyberBattleEnv
from adversa_agentic_ai.api.schemas.sim_models import SimModel, Node, Vulnerability, OutcomeType
from adversa_agentic_ai.models.model_interface import ModelInterface
from adversa_agentic_ai.utils.config_logger import get_agent_logger
from typing import Dict, List, Any

logger = get_agent_logger()

class ConvertedSimModel(ModelInterface):
    def __init__(self, model: SimModel):
        self.name = model.name
        self.a3_services = []
        self.a3_nodes = {}
        self.a3_vulnerabilities = {}
        logger.info(f"Converting Adversa model to CBSim Model: {model.name}")
        self.a3_default_firewall = m.FirewallConfiguration(
            incoming=[
                m.FirewallRule("HTTPS", m.RulePermission.ALLOW),
                m.FirewallRule("SSH", m.RulePermission.ALLOW)
            ],
            outgoing=[
                m.FirewallRule("HTTPS", m.RulePermission.ALLOW)
            ]
        )
        # Deep copy to modify inline
        self.a3_model = copy.deepcopy(model)
        a3_vuln_library = {}  # Will be filled during inference
        for a3_node in self.a3_model.nodes:
            for a3_vuln in a3_node.vulnerabilities:
                try:
                    outcome = self._create_vulnerability_outcome(a3_vuln.outcome_type, **(a3_vuln.outcome_params or {}))
                except Exception as e:
                    logger.error(f"Invalid outcome_params for {a3_vuln.id} in node {a3_node.id}: {e}")
                    outcome = m.ExploitFailed()
                a3_vuln.outcome = outcome  # Inject resolved outcome
        for a3_node in self.a3_model.nodes:
            logger.debug(f"Converting node: {a3_node.id}")
            node_info = self._convert_node(a3_node, a3_vuln_library)
            self.a3_nodes[a3_node.id] = node_info
        self.a3_network = m.create_network(self.a3_nodes)
        for a3_node in self.a3_model.nodes:
            for child_id in a3_node.children:
                self.a3_network.add_edge(a3_node.id, child_id)
        self.a3_identifiers = m.infer_constants_from_nodes(self.a3_nodes.items(), a3_vuln_library)
        self.a3_env = m.Environment(
            network=self.a3_network,
            vulnerability_library=a3_vuln_library,
            identifiers=self.a3_identifiers
        )
        # Validation: Check all LeakedCredentials have credentials
        for vuln_id, vuln in self.a3_vulnerabilities.items():
            if isinstance(vuln.outcome, m.LeakedCredentials):
                if not vuln.outcome.credentials:
                    logger.error(f"LeakedCredentials for vuln {vuln_id} has empty credentials list!")
        self.print_model_info()
        logger.info(f"CBSim Model initialized : {model.name}")

    def _create_vulnerability_outcome(self, outcome_type: OutcomeType, **kwargs) -> m.VulnerabilityOutcome:
        logger.debug(f"Converting outcome type: {outcome_type}")
        match outcome_type:
            case OutcomeType.CustomerData:
                return m.CustomerData()
            case OutcomeType.LateralMove:
                return m.LateralMove(success=kwargs.get("success", True))
            case OutcomeType.PrivilegeEscalation:
                return m.PrivilegeEscalation(level=kwargs["level"])
            case OutcomeType.AdminEscalation:
                return m.AdminEscalation()
            case OutcomeType.SystemEscalation:
                return m.SystemEscalation()
            case OutcomeType.ProbeSucceeded:
                return m.ProbeSucceeded(discovered_properties=kwargs["discovered_properties"])
            case OutcomeType.ProbeFailed:
                return m.ProbeFailed()
            case OutcomeType.ExploitFailed:
                return m.ExploitFailed()
            case OutcomeType.LeakedCredentials:
                raw_credentials = kwargs.get("credentials", [])
                if not raw_credentials:
                    logger.warning("LeakedCredentials has no credentials defined — this will cause CBSim to fail.")
                    raise ValueError("LeakedCredentials outcome must have non-empty 'credentials'")
                credentials = [
                    m.CachedCredential(
                        node=cred["node"],
                        port=cred["port"],
                        credential=cred["credential"]
                    ) for cred in raw_credentials
                ]
                return m.LeakedCredentials(credentials=credentials)
            case OutcomeType.LeakedNodesId:
                return m.LeakedNodesId(nodes=kwargs["nodes"])
            case _:
                raise ValueError(f"Unsupported OutcomeType: {outcome_type}")

    def _infer_cbsim_vuln_type(self, vuln_type: str, vuln_subtype: str) -> m.VulnerabilityType:
        remote_like = {
            "RemoteCodeExecution", "Eavesdropping", "Misconfiguration", "DenialOfService"
        }
        local_like = {
            "PrivilegeEscalation", "CredentialLeak", "SocialEngineering", "PhysicalAttack"
        }
        if vuln_subtype in remote_like:
            return m.VulnerabilityType.REMOTE
        elif vuln_subtype in local_like:
            return m.VulnerabilityType.LOCAL
        type_based_map = {
            "network": m.VulnerabilityType.REMOTE,
            "software": m.VulnerabilityType.REMOTE,
            "social": m.VulnerabilityType.LOCAL,
            "physical": m.VulnerabilityType.LOCAL
        }
        return type_based_map.get(vuln_type.lower(), m.VulnerabilityType.REMOTE)

    def _convert_node(self, node: Node, a3_vuln_library: Dict[str, m.VulnerabilityInfo]) -> m.NodeInfo:
        services = [m.ListeningService(self._map_service_to_port(s.name)) for s in node.services]
        firewall = self.a3_default_firewall if node.firewalls else m.FirewallConfiguration([], [])
        vuln_map = {}
        for v in node.vulnerabilities:
            if not v.outcome:
                raise ValueError(f"Missing outcome in vulnerability {v.id} of node {node.id}")
            cbsim_vuln = m.VulnerabilityInfo(
                description=v.description,
                type=self._infer_cbsim_vuln_type(v.type, v.subtype),
                outcome=v.outcome,
                reward_string=v.description,
                cost=v.cost
            )
            unique_id = f"{node.id}:{v.id}"
            vuln_map[unique_id] = cbsim_vuln
            self.a3_vulnerabilities[unique_id] = cbsim_vuln
            a3_vuln_library[unique_id] = cbsim_vuln

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

    def print_model_info(self):
        print("\n=== [ConvertedSimModel] Internal State ===")
        print(f"Model name: {self.name}")
        print(f"Total services: {len(self.a3_services)}")
        print(f"Total nodes: {len(self.a3_nodes)}")
        print(f"Total vulnerabilities: {len(self.a3_vulnerabilities)}")
        print(f"Identifiers: {self.a3_identifiers}")
        print("\n-- Nodes --")
        for node_id, node in self.a3_nodes.items():
            print(f"Node ID: {node_id}")
            print(f"  Properties: {node.properties}")
            print(f"  Services: {[s.name for s in node.services]}")
            print(f"  Vulnerabilities: {list(node.vulnerabilities.keys())}")

        print("\n-- Vulnerabilities --")
        for vid, vuln in self.a3_vulnerabilities.items():
            print(f"Vulnerability ID: {vid}")
            print(f"  Desc: {vuln.description}")
            print(f"  Type: {vuln.type}")
            print(f"  Outcome: {type(vuln.outcome).__name__}")
            if isinstance(vuln.outcome, m.LeakedCredentials):
                for cred in vuln.outcome.credentials:
                    print(f"    -> Credential: node={cred.node}, port={cred.port}, value={cred.credential}")

        print("\n=== [CBSim Environment View] ===")
        print(f"  Network nodes: {list(self.a3_env.network.nodes)}")
        print(f"  Vulnerability library size: {len(self.a3_env.vulnerability_library)}")

        leaked_creds_found = []
        for v in self.a3_env.vulnerability_library.values():
            if isinstance(v.outcome, m.LeakedCredentials):
                leaked_creds_found.append(v.outcome.credentials)
                print(f"[CBSim] LeakedCredentials found: {[(c.node, c.port, c.credential) for c in v.outcome.credentials]}")

        print(f"\nTotal LeakedCredentials entries in CBSim: {len(leaked_creds_found)}")

    # ModelInterface methods
    def get_env(self):
        return self.a3_env

    def get_model(self):
        return self

    def get_services(self):
        return self.a3_services

    def get_vulnerabilities(self):
        return list(self.a3_vulnerabilities.values())

    def get_nodeinfo(self):
        return self.a3_nodes
