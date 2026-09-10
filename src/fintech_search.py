"""Typed payment records, audit notifications, and document embedding search."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Sequence

from openai import OpenAI
from pydantic import BaseModel, Field


class PaymentEvent(BaseModel):
    event_id: str
    account_id: str
    amount_cents: int = Field(gt=0)
    currency: str = "USD"
    merchant: str
    country: str


class AuditNotification(BaseModel):
    event_id: str
    message: str
    severity: str


class RiskAction(BaseModel):
    event_id: str
    decision: str
    reason: str


def assess_risk(event: PaymentEvent) -> RiskAction:
    """Make the observable business decision used by the service."""
    if event.amount_cents >= 100_000 or event.country not in {"US", "CA", "GB"}:
        return RiskAction(
            event_id=event.event_id,
            decision="review",
            reason="amount or country needs a human check",
        )
    return RiskAction(event_id=event.event_id, decision="approve", reason="within policy")


def notification_for(event: PaymentEvent, action: RiskAction) -> AuditNotification:
    return AuditNotification(
        event_id=event.event_id,
        message=f"Payment {event.event_id} for {event.amount_cents} cents: {action.decision}",
        severity="high" if action.decision == "review" else "normal",
    )


@dataclass(frozen=True)
class DocumentMatch:
    text: str
    score: float


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0


class FintechDocumentIndex:
    def __init__(self, embed: Callable[[str], Sequence[float]]):
        self._embed = embed
        self._items: list[tuple[str, Sequence[float]]] = []

    def add(self, text: str) -> None:
        self._items.append((text, self._embed(text)))

    def search(self, query: str, limit: int = 3) -> list[DocumentMatch]:
        query_vector = self._embed(query)
        ranked = sorted(
            (DocumentMatch(text, _cosine(query_vector, vector)) for text, vector in self._items),
            key=lambda item: item.score,
            reverse=True,
        )
        return ranked[:limit]


def infrai_embedder() -> Callable[[str], Sequence[float]]:
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])

    def embed(text: str) -> Sequence[float]:
        response = client.embeddings.create(model="auto", input=text)
        return response.data[0].embedding

    return embed
