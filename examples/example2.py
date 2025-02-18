from llmutil import chat

output = chat(
    [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "tell me a joke"},
    ],
    model="gpt-4o-mini",
)
print(output)
