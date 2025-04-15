import json
from typing import Callable


def do_function_call(function_call, tools):
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

    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": str(result),
    }


def use_tools(new_response_fn, messages, tools):
    messages = messages.copy()
    ret = None
    while True:
        res = new_response_fn(messages)
        pending = []
        for output in res.output:
            match output.type:
                case "function_call":
                    function_call = {
                        "type": "function_call",
                        "name": output.name,
                        "call_id": output.call_id,
                        "arguments": output.arguments,
                    }
                    pending.append(function_call)
                    messages.append(function_call)
                case "message":
                    ret = output.content[0].text
                case _:
                    assert False, f"unexpected output {output.type}"
        if len(pending) == 0:
            return ret
        for function_call in pending:
            function_call_output = do_function_call(function_call, tools)
            messages.append(function_call_output)
