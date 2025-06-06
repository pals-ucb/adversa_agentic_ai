# File: src/api/stores/prompt_template_store.py

from typing import Dict, List, Optional
from ..schemas.prompt_templates import PromptTemplate
from .file_store import FileStore
from fastapi import BackgroundTasks

class PromptTemplateStore:
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._pstore = FileStore[PromptTemplate]("data/prompt_templates", PromptTemplate)

    def get(self, template_id: str) -> Optional[PromptTemplate]:
        return self.templates.get(template_id)

    def save(self, template: PromptTemplate, background_tasks: BackgroundTasks) -> PromptTemplate:
        self.templates[template.id] = template
        background_tasks.add_task(self._pstore.save, template)
        return template

    def update(self, template_id: str, template: PromptTemplate, background_tasks: BackgroundTasks) -> PromptTemplate:
        self.templates[template_id] = template
        background_tasks.add_task(self._pstore.save, template)
        return template

    def delete(self, template_id: str, background_tasks: BackgroundTasks):
        self.templates.pop(template_id, None)
        background_tasks.add_task(self._pstore.delete, template_id)

    def list_all(self, background_tasks: BackgroundTasks) -> List[PromptTemplate]:
        return list(self.templates.values())
