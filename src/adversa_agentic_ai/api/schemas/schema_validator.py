import logging
from adversa_agentic_ai.api.schemas.sim_models import SimModel
from adversa_agentic_ai.utils.config_logger import get_agent_logger

logger = get_agent_logger()

SUPPORTED_OUTCOME_TYPES = {
    "PrivilegeEscalation",
    "LeakedCredentials",
    "LeakedNodesId",
    "CustomerData",
    "LateralMove",
    "ProbeSucceeded",
    "ProbeFailed",
    "ExploitFailed"
}

def validate_sim_model(model: SimModel) -> None:
    logger.info(f"Starting validation for model: {model.name}")
    node_ids = {node.id for node in model.nodes}

    for node in model.nodes:
        logger.debug(f"Validating node: {node.id}")
        # Validate child references
        for child_id in node.children:
            if child_id not in node_ids:
                logger.error(f"Invalid child_id '{child_id}' in node '{node.id}'")
                raise ValueError(f"Invalid child_id '{child_id}' in node '{node.id}'")

        # Validate each vulnerability
        for vuln in node.vulnerabilities:
            logger.debug(f"Validating vulnerability: {vuln.id}")
            if not vuln.outcome_type:
                logger.error(f"Missing outcome_type in vulnerability '{vuln.id}'")
                raise ValueError(f"Missing outcome_type in vulnerability '{vuln.id}'")

            if not vuln.outcome_params:
                logger.error(f"Missing outcome_params in vulnerability '{vuln.id}'")
                raise ValueError(f"Missing outcome_params in vulnerability '{vuln.id}'")

            if vuln.outcome_type not in SUPPORTED_OUTCOME_TYPES:
                logger.error(f"Unsupported outcome_type '{vuln.outcome_type}' in vulnerability '{vuln.id}'")
                raise ValueError(
                    f"Unsupported outcome_type '{vuln.outcome_type}' in vulnerability '{vuln.id}'"
                )

    logger.info(f"Validation completed successfully for model: {model.name}")
