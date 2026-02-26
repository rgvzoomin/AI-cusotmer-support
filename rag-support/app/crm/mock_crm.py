from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from app.crm.crm_adapter import CRMAdapter


class MockCRMAdapter(CRMAdapter):
    """Simple filesystem-backed mock CRM integration."""

    def __init__(self, log_path: str = './data/crm_mock.log') -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, action: str, payload: dict[str, Any]) -> None:
        line = f"{datetime.utcnow().isoformat()} | {action} | {payload}\n"
        with self.log_path.open('a', encoding='utf-8') as f:
            f.write(line)

    def create_ticket(self, customer_id: str, subject: str, description: str) -> dict[str, Any]:
        ticket_id = f"MOCK-{int(datetime.utcnow().timestamp())}"
        payload = {'ticket_id': ticket_id, 'customer_id': customer_id, 'subject': subject, 'description': description}
        self._write('create_ticket', payload)
        return payload

    def update_ticket(self, ticket_id: str, status: str) -> dict[str, Any]:
        payload = {'ticket_id': ticket_id, 'status': status}
        self._write('update_ticket', payload)
        return payload

    def add_note(self, ticket_id: str, note: str) -> dict[str, Any]:
        payload = {'ticket_id': ticket_id, 'note': note}
        self._write('add_note', payload)
        return payload
