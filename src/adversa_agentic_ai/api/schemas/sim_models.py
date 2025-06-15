# File: src/api/routers/sim_models.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

router = APIRouter()

class VulnerabilityClass(str, Enum):
    discovered = "discovered"          # Found during a scan
    configured = "configured"          # Explicitly configured vulnerability
    exposed = "exposed"                # Directly reachable/exploitable
    lateral_exposed = "lateral-exposed" # Exploitable via another compromised node

class VulnerabilityType(str, Enum):
    software = "software"              # Code-based or dependency vulnerabilities
    network = "network"                # Network-layer misconfiguration or flaw
    social = "social"                  # Human or phishing-based entry points
    physical = "physical"              # Physical access threats

class VulnerabilitySubtype(str, Enum):  # 1:1 mapping with CBSim types
    RemoteCodeExecution = "RemoteCodeExecution"
    PrivilegeEscalation = "PrivilegeEscalation"
    CredentialLeak = "CredentialLeak"
    Eavesdropping = "Eavesdropping"
    DenialOfService = "DenialOfService"
    SocialEngineering = "SocialEngineering"
    Misconfiguration = "Misconfiguration"
    PhysicalAttack = "PhysicalAttack"

class OutcomeType(str, Enum):
    """
    Enumerates the types of outcomes a vulnerability can cause in CyberBattleSim.
    These are mapped to concrete classes like PrivilegeEscalation, LeakedCredentials, etc.
    """
    privilege_escalation = "PrivilegeEscalation"
    leaked_credentials = "LeakedCredentials"
    leaked_nodes = "LeakedNodesId"
    customer_data = "CustomerData"
    lateral_move = "LateralMove"
    probe_succeeded = "ProbeSucceeded"
    probe_failed = "ProbeFailed"
    exploit_failed = "ExploitFailed"

class Vulnerability(BaseModel):
    id: str = Field(..., description="Unique identifier for this vulnerability")
    type: VulnerabilityType = Field(..., description="Type of vulnerability as described in enum above.")
    subtype: VulnerabilitySubtype = Field(..., description="Detailed type (CBSim compatible)")
    description: str = Field(..., description="Detailed explanation of the vulnerability")
    vclass: VulnerabilityClass = Field(..., description="Vulnerability classification level identify if this vulnerability was discovered by the LLM.")
    outcome: str = Field(..., description="Expected effect if exploited (e.g., access granted, DoS)")
    cost: float = Field(default=1.0, description="Cost to exploit this vulnerability")
    granted_access: str = Field(default="user", description="Access level granted upon successful exploitation")
    prereq: Optional[List[str]] = Field(default_factory=list, description="Credentials required before exploitation")
    outcome_type: OutcomeType = Field(..., description="The type of effect this vulnerability has when exploited, mapped to CBSim outcome classes")
    outcome_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Parameter dictionary to instantiate the corresponding outcome object (e.g., {'level': 'admin'} for PrivilegeEscalation)"
    )

class FirewallType(str, Enum):
    linux_fw = "classic linux firewall"        # iptables, nftables, etc.
    phishing_blocker = "phishing-blocker"      # Detects email/social phishing
    mail_filter = "mail-filter"                # Email-based content filter

class Firewall(BaseModel):
    type: FirewallType = Field(..., description="Type of firewall deployed on the node")
    resource: str = Field(..., description="Resource or interface the firewall protects")

class NodeProperty(BaseModel):
    key: str = Field(..., description="Name of the system property (e.g., OS, kernel)")
    version: Optional[str] = Field(None, description="Optional version of the property")
    value: str = Field(..., description="Value for the property")

class NodeService(BaseModel):
    name: str = Field(..., description="Service name (e.g., sshd, apache)")
    description: Optional[str] = Field(None, description="Short explanation of the service")

class NodeResource(BaseModel):
    name: str = Field(..., description="Name of the resource (e.g., port, path, disk)")
    kind: str = Field(..., description="Type/category of resource (e.g., socket, file, endpoint)")
    metadata: Optional[dict] = Field(None, description="Additional details (e.g., encryption, format)")

class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    name: str = Field(..., description="Descriptive name for the node")
    properties: List[NodeProperty] = Field(default_factory=list, description="Static attributes or configuration details")
    services: List[NodeService] = Field(default_factory=list, description="Running services offered by the node")
    resources: List[NodeResource] = Field(default_factory=list, description="Resources hosted or attached to this node")
    constraints: Optional[dict] = Field(None, description="Placement or operational constraints (e.g., region, OS)")
    children: List[str] = Field(default_factory=list, description="Child node IDs (e.g., VMs inside host, microservices)")
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="Vulnerabilities associated with this node")
    firewalls: List[Firewall] = Field(default_factory=list, description="Firewalls or protections deployed on this node")
    value: Optional[float] = Field(default=1.0, description="Reward value if this node is successfully compromised")
    credentials: Optional[List[str]] = Field(default_factory=list, description="List of credentials that work on this node")


class SimModel(BaseModel):
    id: str = Field(..., description="Unique simulation model ID")
    name: str = Field(..., description="Human-readable name for the simulation model")
    description: Optional[str] = Field(None, description="Optional high-level description of the simulation environment")
    nodes: List[Node] = Field(..., description="List of all nodes that compose the simulation environment")
