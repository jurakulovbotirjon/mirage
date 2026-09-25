import pytest

from mirage.core.application import MirageApplication


@pytest.mark.asyncio
async def test_application_processes_user_input() -> None:
    application = MirageApplication()

    response = await application.process("Hello MIRAGE")

    assert response.provider == "mock"
    assert response.model == "mock-model"
    assert response.text == "MIRAGE received: Hello MIRAGE"
