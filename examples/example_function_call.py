from llmutil import FunctionCallOutput, new_response


def add(a, b):
    return a + b


tools = {
    "add": {
        "a": "number",
        "b": "number",
    }
}


def on_function_call(m):
    match m:
        case {"name": "add", "args": {"a": a, "b": b}}:
            return FunctionCallOutput(add(a, b))


messages = [
    {
        "role": "system",
        "content": "you cannot do math. you must use the add() function to add numbers.",
    },
    {
        "role": "user",
        "content": "alice has 10 apples, bob has 20 apples, how many apples do they have in total?",
    },
]

output = new_response(
    messages, model="o4-mini-2025-04-16", tools=tools, on_function_call=on_function_call
)

# Alice and Bob have 30 apples in total.
print(output)
