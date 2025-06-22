# src/aurora/core/context_engine.py
import os
import json
import glob
import yaml
import uuid
from datetime import datetime, timezone

class ContextEngine:
    def __init__(self, eskb_path="eskb"):
        self.eskb_path = os.path.abspath(eskb_path)
        self.event_log_path = os.path.join(self.eskb_path, "event_log.jsonl")
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self) -> dict:
        knowledge = {"events": [], "yaml_data": {}}
        if os.path.exists(self.event_log_path):
            with open(self.event_log_path, "r", encoding="utf-8") as f:
                knowledge["events"] = [json.loads(line) for line in f if line.strip()]
        for yaml_file in glob.glob(os.path.join(self.eskb_path, "*.yaml")):
            with open(yaml_file, "r", encoding="utf-8") as f:
                key = os.path.basename(yaml_file).split('.')[0]
                knowledge["yaml_data"][key] = yaml.safe_load(f)
        return knowledge

    def get_context_for_task(self, task_description: str) -> str:
        keywords = task_description.lower().split()
        relevant_events = [
            e for e in self.knowledge["events"]
            if any(kw in e.get("summary", "").lower() for kw in keywords)
        ]
        context = "### Histórico Relevante:\n"
        if not relevant_events:
            context += "- Nenhum evento relevante encontrado.\n"
        for event in relevant_events[-5:]:
            context += f"- [{event.get('timestamp')}] {event.get('event_type')}: {event.get('summary')} (Status: {event.get('status')})\n"
        context += "\n### Nova Tarefa:"
        return context

    def log_event(self, event_data: dict):
        required_fields = {"event_type", "task_id", "status", "summary"}
        if not required_fields.issubset(event_data):
            raise ValueError("Evento incompleto. Faltam campos obrigatórios.")
        event_data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        event_data.setdefault("event_id", f"evt_{uuid.uuid4().hex[:16]}")
        with open(self.event_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + "\n")