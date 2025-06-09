import sys
import os
import cyberbattle.simulation.model as m
from cyberbattle._env.cyberbattle_env import CyberBattleEnv
from typing import Dict
from adversa_agentic_ai.models.model_interface import ModelInterface

class ErSimModel(ModelInterface):
    def __init__(self):
        self.name = "ErSim" 
        self.services = []
        # Shared components
        self.default_allow = [
            m.FirewallRule("HTTPS", m.RulePermission.ALLOW),
            m.FirewallRule("SSH", m.RulePermission.ALLOW)
        ]       
        self.phishing_vuln = m.VulnerabilityInfo(
            description="Phishing link clicked",
            type=m.VulnerabilityType.LOCAL,
            outcome=m.LeakedCredentials(credentials=[
                m.CachedCredential(node="CheckInStation", port="HTTPS", credential="checkin-user-creds")
            ]),
            reward_string="Credentials leaked via phishing",
            cost=1.0
        )
        self.misconfig_vuln = m.VulnerabilityInfo(
            description="Public API exposed sensitive data",
            type=m.VulnerabilityType.REMOTE,
            outcome=m.CustomerData(),
            reward_string="PHI accessed via API misconfig",
            cost=2.0
        )
        self.vulnerabilities = [self.phishing_vuln, self.misconfig_vuln]
        # All nodes
        self.nodes = {
            "Patient": m.NodeInfo(
                services=[],
                firewall=m.FirewallConfiguration(incoming=[], outgoing=[]),
                value=10,
                properties=["Human", "Role:Patient"],
                vulnerabilities={"phishing": self.phishing_vuln},
                agent_installed=False,
                reimagable=False
            ),
            "Nurse": m.NodeInfo(
                services=[],
                firewall=m.FirewallConfiguration(incoming=[], outgoing=self.default_allow),
                value=30,
                properties=["Human", "Role:Nurse"],
                vulnerabilities={"phishing": self.phishing_vuln},
                agent_installed=False,
                reimagable=False
            ),
            "Doctor": m.NodeInfo(
                services=[],
                firewall=m.FirewallConfiguration(incoming=[], outgoing=self.default_allow),
                value=50,
                properties=["Human", "Role:Doctor"],
                vulnerabilities={"phishing": self.phishing_vuln},
                agent_installed=False,
                reimagable=False
            ),
            "CheckInStation": m.NodeInfo(
                services=[m.ListeningService("HTTPS")],
                firewall=m.FirewallConfiguration(incoming=self.default_allow, outgoing=self.default_allow),
                value=40,
                properties=["Ubuntu", "PHI", "EHRAccess"],
                vulnerabilities={"misconfig": self.misconfig_vuln},
                agent_installed=True,
                reimagable=True
            ),
            "TriageStation": m.NodeInfo(
                services=[m.ListeningService("HTTPS")],
                firewall=m.FirewallConfiguration(incoming=self.default_allow, outgoing=self.default_allow),
                value=30,
                properties=["Ubuntu", "VitalsCapture"],
                vulnerabilities={"misconfig": self.misconfig_vuln},
                agent_installed=True,
                reimagable=True
            ),
            "Laboratory": m.NodeInfo(
                services=[m.ListeningService("HTTPS"), m.ListeningService("SQL")],
                firewall=m.FirewallConfiguration(incoming=self.default_allow, outgoing=self.default_allow),
                value=60,
                properties=["LabData", "PHI"],
                vulnerabilities={"misconfig": self.misconfig_vuln},
                agent_installed=True,
                reimagable=True
            ),
            "Pharmacy": m.NodeInfo(
                services=[m.ListeningService("HTTPS")],
                firewall=m.FirewallConfiguration(incoming=self.default_allow, outgoing=self.default_allow),
                value=45,
                properties=["PrescriptionSystem"],
                vulnerabilities={"misconfig": self.misconfig_vuln},
                agent_installed=True,
                reimagable=True
            ),
            "ERBilling": m.NodeInfo(
                services=[m.ListeningService("HTTPS"), m.ListeningService("SQL")],
                firewall=m.FirewallConfiguration(incoming=self.default_allow, outgoing=self.default_allow),
                value=70,
                properties=["Billing", "PII"],
                vulnerabilities={"misconfig": self.misconfig_vuln},
                agent_installed=True,
                reimagable=True
            )
        }

        for node, node_attribs in self.nodes.items():
            print(f'Node: {node}, type: {node_attribs.properties}')

        # --- Define Environment ---
        vulnerability_library = {}
        ENV_IDENTIFIERS = m.infer_constants_from_nodes(self.nodes.items(), vulnerability_library)
        self.network = m.create_network(self.nodes)

        # Add edges to define topology (example flow)
        self.network.add_edge("Patient", "CheckInStation")
        self.network.add_edge("CheckInStation", "TriageStation")
        self.network.add_edge("TriageStation", "Laboratory")
        self.network.add_edge("TriageStation", "Doctor")
        self.network.add_edge("Doctor", "Pharmacy")
        self.network.add_edge("Doctor", "ERBilling")
        self.network.add_edge("Nurse", "TriageStation")
        self.network.add_edge("Doctor", "Laboratory")

        self.env = m.Environment(
            network=self.network,
            vulnerability_library=vulnerability_library,
            identifiers=ENV_IDENTIFIERS
        )

    def get_env(self):
        return self.env
    
    def get_model(self):
        return self
    
    def get_services(self):
        return self.services
    
    def get_vulnerabilities(self):
        return self.vulnerabilities
    
    def get_nodeinfo(self):
        return self.nodes

'''


sim = CyberBattleEnv(env)

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

'''