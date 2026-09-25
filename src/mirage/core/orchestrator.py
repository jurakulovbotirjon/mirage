from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from mirage.models.base import ModelProvider, ModelRequest, ModelResponse


@dataclass(frozen=True, slots=True)
class Task:
    id: UUID
    user_input: str


class Orchestrator:
    def __init__(self, model_provider: ModelProvider) -> None:
        self._model_provider = model_provider

    async def handle(self, user_input: str) -> tuple[Task, ModelResponse]:
        task = Task(
            id=uuid4(),
            user_input=user_input,
        )

        request = ModelRequest(
            prompt=user_input,
        )

        response = await self._model_provider.generate(request)

        return task, response
