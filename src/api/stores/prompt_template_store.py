# File: src/api/stores/prompt_template_store.py

from typing import Dict, List, Optional
from ..schemas.prompt_templates import PromptTemplate

class PromptTemplateStore:
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}

    def get(self, template_id: str) -> Optional[PromptTemplate]:
        return self.templates.get(template_id)

    def save(self, template: PromptTemplate) -> PromptTemplate:
        self.templates[template.id] = template
        return template

    def update(self, template_id: str, updated: PromptTemplate) -> PromptTemplate:
        self.templates[template_id] = updated
        return updated

    def delete(self, template_id: str):
        self.templates.pop(template_id, None)

    def list_all(self) -> List[PromptTemplate]:
        return list(self.templates.values())
