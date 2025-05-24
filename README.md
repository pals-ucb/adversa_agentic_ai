# Adversa Agentic AI Simulation Platform for Security Compliance

## Overview

This project implements a modular, agentic-AI-driven red/blue simulation environment for domain-specific security compliance evaluation. Built on top of a forked version of Microsoft's CyberBattleSim, the platform simulates realistic organizational environments (e.g., ER facilities, web infrastructures) and embeds red/blue agents using LLMs (e.g., Claude, LLaMA). It provides a programmable interface for modeling vulnerabilities, simulating threats, and evaluating compliance posture under adversarial pressure.

---

## Table of Contents

| Section                   | Link                                                     |
| ------------------------- | -------------------------------------------------------- |
| Problem Statement         | [#problem-statement](#problem-statement)                 |
| Solution Overview         | [#solution-overview](#solution-overview)                 |
| Architecture              | [#architecture](#architecture)                           |
| Getting Started           | [#getting-started](#getting-started)                     |
| Repository Organization   | [#repository-organization](#repository-organization)     |
| Development Practices     | [#development-practices](#development-practices)         |
| Modeling                  | [#modeling](#modeling)                                   |
| Vulnerability Description | [#vulnerability-description](#vulnerability-description) |
| Services Description      | [#services-description](#services-description)           |
| Simulation                | [#simulation](#simulation)                               |
| Agent Development         | [#agent-development](#agent-development)                 |
| Testing                   | [#testing](#testing)                                     |

---

## Problem Statement

Security compliance is often measured through static audits, which fail to account for dynamic threats and adversarial behavior. Organizations lack simulation environments to proactively test and harden their security posture against real-world attacks in the context of HIPAA, PCI-DSS, or other compliance frameworks.

---

## Solution Overview

We introduce "Adversa Agentic AI (A3)", a simulation infrastructure for:

* Modeling enterprise environments (e.g., hospitals, finance)
* Embedding adversarial red and defensive blue agents
* Injecting domain-specific vulnerabilities
* Validating compliance control coverage through attack-defense simulations

Built on CyberBattleSim and enhanced with LLM-based agents and domain knowledge, the platform simulates both technical and policy-based violations in real-time.

---

## Architecture

```
+--------------------------------------------+
|       Agentic AI Simulation Platform       |
+--------------------------------------------+
| Simulation Engine (CyberBattleSim Fork)    |
| + Environment Topology Loader              |
| + Node & Vulnerability Models              |
+--------------------------------------------+
| Agent Layer (LLMs / Scripted)              |
| + Red Agents (External + Internal)         |
| + Blue Agents (Detection + Response)       |
+--------------------------------------------+
| AWS LLM Connectors (Claude, Bedrock, etc.) |
+--------------------------------------------+
```

---

## Getting Started

### Set-Up (Ubuntu + Conda)

```bash
sudo apt install git python3 python3-pip
conda create -n cbsim python=3.10 -y
conda activate cbsim
```

### Install CyberBattleSim fork

```bash
git clone --recurse-submodules git@github.com:pals-ucb/adversa-agentic-ai.git
cd adversa-agentic-ai/modules/agentic_cbsim
pip install -e .[dev]
```

### Run Test Environment

```bash
cd ../../sims/tests
python basic_env_test.py
```

---

## Repository Organization

```
agentic-ai/
├── modules/agentic_cbsim/     # CyberBattleSim fork
├── sims/healthcare/           # ER domain environment models
├── agents/                    # LLM-based or scripted red/blue agents
├── scripts/                   # Automation or training
├── tests/                     # Unit and integration tests
├── requirements.txt
└── README.md
```

---

## Development Practices

* All new development should occur on a feature branch off `dev`
* Use signed commits with GPG key:

```bash
git config commit.gpgsign true
git config user.signingkey <your-key-id>
```

* Submit pull requests for code review and merge to `main` only via PR

---

## Modeling

Each domain model (e.g., ER) contains:

* Devices (terminals, servers, kiosks)
* Human nodes (patients, doctors, nurses)
* Logical connections and access rules
* Labeled node properties, values, and vulnerabilities

---

## Vulnerability Description

Vulnerabilities are modeled using `VulnerabilityInfo`:

* `phishing`, `public_api`, `ssh_misconfig`, etc.
* Outcomes include credential leakage, data exfiltration, lateral movement

---

## Services Description

Nodes host services (HTTPS, SQL, FHIR-API). Firewalls model allowed/blocked communication. Properties can influence exploitability.

---

## Simulation

We use `CyberBattleEnv` to:

* Load environment graphs
* Step through attacker/defender policies
* Simulate random or guided attack paths
* Output logs and rewards

---

## Agent Development

Agents are implemented under `agents/`:

* `red_agent_llm.py`: Red agent using Bedrock/Claude
* `blue_agent_policy.py`: Blue agent for compliance enforcement
* Uses modular interface to interact with CBSim env

---

## Testing

Test scripts located in `tests/`:

* Environment validation
* Agent step function correctness
* Episode termination conditions

To run:

```bash
pytest tests/
```

---

*This README will evolve as new modules and domains are added.*

