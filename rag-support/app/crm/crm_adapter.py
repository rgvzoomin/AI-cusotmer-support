from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CRMAdapter(ABC):
    @abstractmethod
    def create_ticket(self, customer_id: str, subject: str, description: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update_ticket(self, ticket_id: str, status: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def add_note(self, ticket_id: str, note: str) -> dict[str, Any]:
        raise NotImplementedError
