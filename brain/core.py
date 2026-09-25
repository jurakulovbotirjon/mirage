from datetime import datetime

from brain.llm import ask_llm
from memory.store import recall, remember


def think(command: str) -> str:
    command = command.lower().strip()

    # Memory: Remember facts
    if command.startswith("remember "):
        try:
            content = command.replace("remember ", "", 1)

            key, value = content.split(" is ", 1)

            remember(key.strip(), value.strip())

            return f"I will remember that {key} is {value}."

        except ValueError:
            return "Use: remember something is value"

    # Memory: Recall facts
    elif command.startswith("what is "):
        key = command.replace("what is ", "", 1).strip()

        value = recall(key)

        if value:
            return f"{key} is {value}."

    # Built-in commands
    if "time" in command:
        return f"The current time is {datetime.now().strftime('%H:%M')}"

    elif "who are you" in command or "your name" in command:
        return "I am Mirage, your personal AI assistant."

    elif "hello" in command:
        return "Hello, I am Mirage."

    # Fallback to Qwen3
    return ask_llm(command)
