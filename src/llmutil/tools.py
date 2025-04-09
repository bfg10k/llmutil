import json
from typing import Callable


def use_tools(tool_call, tools):
    assert tool_call.__class__.__name__ == "ResponseFunctionToolCall"
    assert isinstance(tools, list)
    for tool in tools:
        assert isinstance(tool, Callable)

    name = tool_call.name
    call_id = tool_call.id
    args = json.loads(tool_call.arguments)

    # find the tool
    fn = None
    for tool in tools:
        if tool.__name__ == name:
            fn = tool
            break
    assert fn is not None

    # call
    result = fn(**args)

    return {
        "type": "function_call_result",
        "call_id": call_id,
        "output": str(result),
    }
