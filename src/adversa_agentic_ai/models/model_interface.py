# models/model_interface.py

from abc import ABC, abstractmethod

class ModelInterface(ABC):
    @abstractmethod
    def get_env(self):
        """Return the simulation environment instance."""
        pass

    @abstractmethod
    def get_vulnerabilities(self):
        """Return the vulnerability definitions used in the model."""
        pass

    @abstractmethod
    def get_services(self):
        """Return the service definitions used in the model."""
        pass

    @abstractmethod
    def get_nodeinfo(self):
        """Return the node information including topology."""
        pass

    @abstractmethod
    def get_model(self):
        """Return a dictionary or object representing the complete model structure for export or inspection."""
        pass
