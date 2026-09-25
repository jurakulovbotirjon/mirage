from __future__ import annotations

from mirage.core.events import EventBus
from mirage.core.orchestrator import Orchestrator
from mirage.models.base import ModelResponse
from mirage.models.mock import MockModelProvider


class MirageApplication:
    def __init__(self) -> None:
        self.events = EventBus()

        provider = MockModelProvider()

        self.orchestrator = Orchestrator(
            model_provider=provider,
        )

    async def process(self, user_input: str) -> ModelResponse:
        _, response = await self.orchestrator.handle(user_input)
        return response
