import sys
import os
import cyberbattle.simulation.model as m
from cyberbattle._env.cyberbattle_env import CyberBattleEnv
from typing import Dict


# Shared components
default_allow = [
    m.FirewallRule("HTTPS", m.RulePermission.ALLOW),
    m.FirewallRule("SSH", m.RulePermission.ALLOW)
]

phishing_vuln = m.VulnerabilityInfo(
    description="Phishing link clicked",
    type=m.VulnerabilityType.LOCAL,
    outcome=m.LeakedCredentials(credentials=[
        m.CachedCredential(node="CheckInStation", port="HTTPS", credential="checkin-user-creds")
    ]),
    reward_string="Credentials leaked via phishing",
    cost=1.0
)

misconfig_vuln = m.VulnerabilityInfo(
    description="Public API exposed sensitive data",
    type=m.VulnerabilityType.REMOTE,
    outcome=m.CustomerData(),
    reward_string="PHI accessed via API misconfig",
    cost=2.0
)

# All nodes
nodes = {
    "Patient": m.NodeInfo(
        services=[],
        firewall=m.FirewallConfiguration(incoming=[], outgoing=[]),
        value=10,
        properties=["Human", "Role:Patient"],
        vulnerabilities={"phishing": phishing_vuln},
        agent_installed=False,
        reimagable=False
    ),
    "Nurse": m.NodeInfo(
        services=[],
        firewall=m.FirewallConfiguration(incoming=[], outgoing=default_allow),
        value=30,
        properties=["Human", "Role:Nurse"],
        vulnerabilities={"phishing": phishing_vuln},
        agent_installed=False,
        reimagable=False
    ),
    "Doctor": m.NodeInfo(
        services=[],
        firewall=m.FirewallConfiguration(incoming=[], outgoing=default_allow),
        value=50,
        properties=["Human", "Role:Doctor"],
        vulnerabilities={"phishing": phishing_vuln},
        agent_installed=False,
        reimagable=False
    ),
    "CheckInStation": m.NodeInfo(
        services=[m.ListeningService("HTTPS")],
        firewall=m.FirewallConfiguration(incoming=default_allow, outgoing=default_allow),
        value=40,
        properties=["Ubuntu", "PHI", "EHRAccess"],
        vulnerabilities={"misconfig": misconfig_vuln},
        agent_installed=True,
        reimagable=True
    ),
    "TriageStation": m.NodeInfo(
        services=[m.ListeningService("HTTPS")],
        firewall=m.FirewallConfiguration(incoming=default_allow, outgoing=default_allow),
        value=30,
        properties=["Ubuntu", "VitalsCapture"],
        vulnerabilities={"misconfig": misconfig_vuln},
        agent_installed=True,
        reimagable=True
    ),
    "Laboratory": m.NodeInfo(
        services=[m.ListeningService("HTTPS"), m.ListeningService("SQL")],
        firewall=m.FirewallConfiguration(incoming=default_allow, outgoing=default_allow),
        value=60,
        properties=["LabData", "PHI"],
        vulnerabilities={"misconfig": misconfig_vuln},
        agent_installed=True,
        reimagable=True
    ),
    "Pharmacy": m.NodeInfo(
        services=[m.ListeningService("HTTPS")],
        firewall=m.FirewallConfiguration(incoming=default_allow, outgoing=default_allow),
        value=45,
        properties=["PrescriptionSystem"],
        vulnerabilities={"misconfig": misconfig_vuln},
        agent_installed=True,
        reimagable=True
    ),
    "ERBilling": m.NodeInfo(
        services=[m.ListeningService("HTTPS"), m.ListeningService("SQL")],
        firewall=m.FirewallConfiguration(incoming=default_allow, outgoing=default_allow),
        value=70,
        properties=["Billing", "PII"],
        vulnerabilities={"misconfig": misconfig_vuln},
        agent_installed=True,
        reimagable=True
    )
}

for node, node_attribs in nodes.items():
    print(f'Node: {node}, type: {node_attribs.properties}')

# --- Define Environment ---
vulnerability_library = {}
ENV_IDENTIFIERS = m.infer_constants_from_nodes(nodes.items(), vulnerability_library)
network = m.create_network(nodes)

# Add edges to define topology (example flow)
network.add_edge("Patient", "CheckInStation")
network.add_edge("CheckInStation", "TriageStation")
network.add_edge("TriageStation", "Laboratory")
network.add_edge("TriageStation", "Doctor")
network.add_edge("Doctor", "Pharmacy")
network.add_edge("Doctor", "ERBilling")
network.add_edge("Nurse", "TriageStation")
network.add_edge("Doctor", "Laboratory")

env = m.Environment(
    network=network,
    vulnerability_library=vulnerability_library,
    identifiers=ENV_IDENTIFIERS
)

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
