from enum import Enum

class BlueAgentActions(str, Enum):
    LOG_EVENT = "log_event"
    PATCH_OS = "patch_os"
    UPGRADE_SOFTWARE = "upgrade_software"
    CLOSE_PORTS_NOT_INUSE = "close_ports_not_inuse"
    ESCALAT_TO_HUMANS = "escalate_to_humans"
    ISOLATE_NODE = "isolate_node"
    CHANGE_PASSWORD = "change_password"
