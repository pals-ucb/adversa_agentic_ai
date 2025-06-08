# File: src/api/stores/prompt_template_store.py

import os
from fastapi import BackgroundTasks
from typing import Dict, List, Optional
from ..schemas.prompt_templates import PromptTemplate
#from .file_store import FileStore
from .s3_store import S3Store




class PromptTemplateStore:
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        #self._pstore = FileStore[PromptTemplate]("data/prompt_templates", PromptTemplate)
        BUCKET = os.getenv("DATA_BUCKET", "adversa-agentic-ai-data")
        PREFIX = os.getenv("PROMPT_TEMPLATES_PREFIX", "prompt_templates")
        self._s3store = S3Store[PromptTemplate](bucket=BUCKET, prefix=PREFIX, model_cls=PromptTemplate)

    def get(self, template_id: str) -> Optional[PromptTemplate]:
        template = None
        template = self.templates.get(template_id)
        if not template:
            template = self._s3store.load(template_id)
            self.templates[template_id] = template
        return template

    def save(self, template: PromptTemplate, background_tasks: BackgroundTasks) -> PromptTemplate:
        self.templates[template.id] = template
        #background_tasks.add_task(self._pstore.save, template)
        #background_tasks.add_task(self._s3store.save, template)
        self._s3store.save(template)
        return template

    def update(self, template_id: str, template: PromptTemplate, background_tasks: BackgroundTasks) -> PromptTemplate:
        self.templates[template_id] = template
        #background_tasks.add_task(self._pstore.save, template)
        #background_tasks.add_task(self._s3store.save, template)
        self._s3store.save(template)
        return template

    def delete(self, template_id: str, background_tasks: BackgroundTasks):
        self.templates.pop(template_id, None)
        #background_tasks.add_task(self._pstore.delete, template_id)
        #background_tasks.add_task(self._s3store.delete, template_id)
        self._s3store.delete(template_id)

    def list_all(self, background_tasks: BackgroundTasks) -> List[PromptTemplate]:
        return list(self.templates.values())
