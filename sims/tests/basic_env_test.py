import networkx as nx
import cyberbattle.simulation.model as m
from cyberbattle._env.cyberbattle_env import CyberBattleEnv

# Define vulnerabilities
scan_vuln = m.VulnerabilityInfo(
    description="Scan vulnerability used to escalate",
    type=m.VulnerabilityType.LOCAL,
    outcome=m.PrivilegeEscalation(level=1),
    reward_string="Scan exploit succeeded: escalated access.",
    cost=1.0
)

exploit_vuln = m.VulnerabilityInfo(
    description="Remote exploit on target",
    type=m.VulnerabilityType.REMOTE,
    outcome=m.LeakedCredentials(
        credentials=[m.CachedCredential(node="target", port="SSH", credential="target-creds")]
    ),
    reward_string="Leaked SSH credentials from target.",
    cost=1.0
)

# Vulnerability library must include a REMOTE vulnerability with LeakedCredentials
vuln_lib = {
    "scan": scan_vuln,
    "exploit": exploit_vuln
}

# Build network
g = nx.Graph()

g.add_node("attacker")
g.nodes["attacker"]["data"] = m.NodeInfo(
    services=[],
    firewall=m.FirewallConfiguration(incoming=[], outgoing=[]),
    value=0,
    properties=["Linux"],
    vulnerabilities={"scan": scan_vuln},
    agent_installed=True,
    reimagable=False
)

g.add_node("target")
g.nodes["target"]["data"] = m.NodeInfo(
    services=[m.ListeningService("SSH", allowedCredentials=["target-creds"])],
    firewall=m.FirewallConfiguration(incoming=[], outgoing=[]),
    value=100,
    properties=["Ubuntu"],
    vulnerabilities={"exploit": exploit_vuln},
    agent_installed=False,
    reimagable=True
)

g.add_edge("attacker", "target")

# Build environment
nodes_with_data = {n: g.nodes[n]["data"] for n in g.nodes}
env = m.Environment(
    network=m.create_network(nodes_with_data),
    vulnerability_library=vuln_lib,
    identifiers=m.infer_constants_from_nodes(nodes_with_data.items(), vuln_lib)
)

# Initialize simulator
sim = CyberBattleEnv(env)

obs = sim.reset()
done = False
total_reward = 0

while not done:
    action = sim.sample_valid_action()
    obs, reward, done, _, info = sim.step(action)
    print(f"Action: {action}, Reward: {reward}")
    total_reward += reward

print("✅ Simulation finished. Total reward:", total_reward)
