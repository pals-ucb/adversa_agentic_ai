from enum import Enum

# Clean this up and keep only generic actions.
class BaseActions(str, Enum):
    port_scan = "port_scan"
    email_phishing = "email_phishing"
    default_credentials_attempt = "default_credentials_attempt"
