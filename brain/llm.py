import ollama

def ask_llm(prompt):
    response = ollama.chat(
        model="qwen3",
        messages=[
            {
                "role": "system",
                "content": """
You are Mirage.

You are a personal AI assistant.
Keep responses concise.
Be helpful.
Remember your name is Mirage.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]
