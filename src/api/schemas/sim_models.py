# File: src/api/routers/sim_models.py
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

router = APIRouter()

class VulnerabilityClass(str, Enum):
    discovered = "discovered"
    configured = "configured"
    exposed = "exposed"
    lateral_exposed = "lateral-exposed"

class VulnerabilityType(str, Enum):
    software = "software"
    network = "network"
    social = "social"
    physical = "physical"

class Vulnerability(BaseModel):
    id: str
    type: VulnerabilityType
    description: str
    vclass: VulnerabilityClass
    outcome: str

class FirewallType(str, Enum):
    linux_fw = "classic linux firewall"
    phishing_blocker = "phishing-blocker"
    mail_filter = "mail-filter"

class Firewall(BaseModel):
    type: FirewallType
    resource: str

class NodeProperty(BaseModel):
    key: str
    version: Optional[str] = None
    value: str

class NodeService(BaseModel):
    name: str
    description: Optional[str] = None

class NodeResource(BaseModel):
    name: str
    kind: str
    metadata: Optional[dict] = None

class Node(BaseModel):
    id: str
    name: str
    properties: List[NodeProperty] = []
    services: List[NodeService] = []
    resources: List[NodeResource] = []
    constraints: Optional[dict] = None
    children: List[str] = []
    vulnerabilities: List[Vulnerability] = []
    firewalls: List[Firewall] = []

class SimModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    nodes: List[Node]

