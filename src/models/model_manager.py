import importlib.util
import os
import sys
import json
from models.model_interface import ModelInterface

class ModelManager:
    def __init__(self):
        self.models = {}  # key -> model_instance

    def add_model(self, module_path: str, model_file_name: str, model_class_name: str) -> str:
        """
        Dynamically load the model module and instantiate the specified class.
        Returns a key used to retrieve this model later.
        """
        full_path = os.path.join(module_path, model_file_name)
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"Model file not found: {full_path}")

        module_name = os.path.splitext(model_file_name)[0]
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, model_class_name):
            raise AttributeError(f"Module {module_name} must define a class named '{model_class_name}'")

        model_class = getattr(module, model_class_name)
        instance = model_class()

        if not isinstance(instance, ModelInterface):
            raise TypeError("Model must implement ModelInterface")

        key = f"{module_name}.{model_class_name}"
        self.models[key] = instance
        return key

    def load_model(self, key: str):
        return self.models.get(key)

    def save_model(self, key: str, filepath: str):
        model = self.models.get(key)
        if not model:
            raise KeyError(f"Model with key '{key}' not found")
        with open(filepath, 'w') as f:
            json.dump(model.get_model(), f, indent=2)

    def update_model(self, key: str, data):
        # Placeholder: Logic to update the model dynamically
        pass

    def get_env(self, key: str):
        return self.models[key].get_env()

    def get_vulnerabilities(self, key: str):
        return self.models[key].get_vulnerabilities()

    def get_services(self, key: str):
        return self.models[key].get_services()

    def get_nodeinfo(self, key: str):
        return self.models[key].get_nodeinfo()

    def get_model(self, key: str):
        return self.models[key].get_model()
    