import json
import types
from typing import Callable

from .client import default_client


def use_tools(function_call, tools):
    assert function_call["type"] == "function_call"
    assert isinstance(tools, list)
    for tool in tools:
        assert isinstance(tool, Callable)

    name = function_call["name"]
    arguments = function_call["arguments"]
    call_id = function_call["call_id"]

    # find the tool
    fn = None
    for tool in tools:
        if tool.__name__ == name:
            fn = tool
            break
    assert fn is not None

    # call
    args = json.loads(arguments)
    result = fn(**args)

    if isinstance(result, types.GeneratorType):
        *intermediates, result = list(result)
    else:
        intermediates = []

    for i in intermediates:
        yield {
            "type": "_intermediate",
            "data": i,
        }
    yield {
        "type": "function_call_output",
        "call_id": call_id,
        "output": str(result),
    }


def get_tool_response(instructions, tools, tools_def, conversation):
    temp_conversation = conversation.copy()
    while True:
        response = default_client().responses.create(
            model="gpt-4o",
            input=[{"role": "system", "content": instructions}, *temp_conversation],
            tools=tools_def,
        )
        pending = []
        for output in response.output:
            temp_conversation.append(output)
            match output.type:
                case "function_call":
                    function_call = {
                        "type": "function_call",
                        "name": output.name,
                        "call_id": output.call_id,
                        "arguments": output.arguments,
                    }
                    pending.append(function_call)
                    yield function_call
                case "message":
                    message = {
                        "role": "assistant",
                        "content": output.content[0].text,
                    }
                    conversation.append(message)
                    yield message | {"type": "message"}
                case _:
                    assert False, "unknown output type: " + output.type
        if len(pending) == 0:
            break
        for function_call in pending:
            for tool_output in use_tools(function_call, tools):
                yield tool_output
                match tool_output["type"]:
                    case "function_call_output":
                        temp_conversation.append(tool_output)
                    case "_intermediate":
                        pass
                    case _:
                        assert False, "unknown output type: " + tool_output["type"]
