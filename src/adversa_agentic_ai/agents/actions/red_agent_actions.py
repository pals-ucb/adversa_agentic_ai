from enum import Enum

class RedAgentActions(str, Enum):
    BRUTE_FORCE_SSH = "brute_force_ssh"
    SQL_INJECTION = "sql_injection"
    EXPLOIT_KNOWN_CVE = "exploit_known_cve"
    CUSTOM_PAYLOAD_UPLOAD = "custom_payload_upload"
    ENUMERATE_USER_ROLES = "enumerate_user_roles"
    FINGERPRINT_WEBSERVER = "fingerprint_webserver"
