import json
from typing import Any, Callable

from openai.types.responses import (
    Response,
    ResponseFunctionToolCallParam,
    ResponseInputItemParam,
)
from openai.types.responses.response_input_item_param import FunctionCallOutput


def do_function_call(
    function_call: ResponseFunctionToolCallParam,
    ctx: dict[str, Any],
    tools: list[Callable[..., str]],
) -> FunctionCallOutput:
    assert isinstance(function_call, dict)
    assert function_call["type"] == "function_call"
    assert isinstance(tools, list)
    assert all(isinstance(tool, Callable) for tool in tools)

    name = function_call["name"]
    arguments = function_call["arguments"]
    call_id = function_call["call_id"]

    # find the tool by name
    selected = None
    for tool in tools:
        if tool.__name__ == name:
            selected = tool
            break
    assert selected is not None, f"cannot find tool {name}"

    # call it
    args = json.loads(arguments)
    result = selected(ctx, **args)
    assert isinstance(result, str), f"expected str, got {type(result)}"

    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": result,
    }


def use_tools(
    new_response_fn: Callable[[list[ResponseInputItemParam]], Response],
    messages: list[ResponseInputItemParam],
    ctx: dict[str, Any],
    tools: list[Callable[..., str]],
):
    """
    Helper function to handle tool (function) calls from LLM responses.

    It:
    - Gets an LLM response.
    - If the response includes a function call, runs the function and adds output to messages.
    - Repeats until no function calls remain.
    - Returns the final content text.

    Messages is a list of input messages. This function doesn't modify it. Users are responsible for adding content output to messages. Function calls and their outputs are not maintained in messages by this function.

    Each tool is a function that takes a context (for debugging) and keyword arguments from the LLM output.

    Args:
        new_response_fn: Function to generate LLM response from messages.
        messages: List of input messages (not modified).
        ctx: Dictionary for storing debug info.
        tools: List of functions that take ctx and keyword args from LLM output.

    Returns:
        Final content text.
    """
    assert isinstance(new_response_fn, Callable)
    assert isinstance(messages, list)
    assert isinstance(ctx, dict)
    assert isinstance(tools, list)
    assert all(isinstance(tool, Callable) for tool in tools)

    messages = messages.copy()

    while True:
        res: Response = new_response_fn(messages)

        ret = None
        pending: list[ResponseFunctionToolCallParam] = []

        for output in res.output:
            match output.type:
                case "function_call":
                    function_call: ResponseFunctionToolCallParam = {
                        "type": "function_call",
                        "name": output.name,
                        "call_id": output.call_id,
                        "arguments": output.arguments,
                    }
                    pending.append(function_call)
                    messages.append(function_call)
                case "message":
                    content = output.content[0]
                    assert content.type == "output_text", (
                        f"unexpected content type {output.type}"
                    )
                    ret = content.text
                case _:
                    assert False, f"unexpected output {output.type}"

        if len(pending) == 0:
            # if no more function calls, return the content text
            # otherwise discard the content text and do function calls
            return ret
        for function_call in pending:
            function_call_output = do_function_call(function_call, ctx, tools)
            messages.append(function_call_output)
