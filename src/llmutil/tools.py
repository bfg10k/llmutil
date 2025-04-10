import json
from typing import Callable

from openai import OpenAI

client = OpenAI()


def use_tools(tool_call, tools):
    assert tool_call.__class__.__name__ == "ResponseFunctionToolCall"
    assert isinstance(tools, list)
    for tool in tools:
        assert isinstance(tool, Callable)

    # find the tool
    fn = None
    for tool in tools:
        if tool.__name__ == tool_call.name:
            fn = tool
            break
    assert fn is not None

    # call
    args = json.loads(tool_call.arguments)
    result = fn(**args)

    return {
        "type": "function_call_output",
        "call_id": tool_call.call_id,
        "output": str(result),
    }


def get_response(instructions, tools, tools_def, conversation):
    temp_conversation = conversation.copy()
    while True:
        response = client.responses.create(
            model="gpt-4o",
            input=[{"role": "system", "content": instructions}, *temp_conversation],
            tools=tools_def,
        )
        has_func_call = False
        for item in response.output:
            if item.type == "function_call":
                has_func_call = True
                tool_output = use_tools(item, tools)
                temp_conversation.append(item)
                temp_conversation.append(tool_output)
        if not has_func_call:
            output = response.output[0]
            assert output.type == "message"
            conversation.append(output)
            return output.content[0].text
