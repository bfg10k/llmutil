import json

from openai import NOT_GIVEN, NotGiven, OpenAI
from openai.types.responses import (
    FileSearchToolParam,
    FunctionToolParam,
    ResponseOutputItem,
    ResponseTextConfigParam,
)
from schemautil import object_schema


class FunctionCallOutput:
    def __init__(self, output):
        self.output = output


_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def build_tools(
    tools, memory: str | None
) -> list[FunctionToolParam | FileSearchToolParam]:
    ret = []
    if tools:
        for name, params in tools.items():
            ret.append(
                {
                    "type": "function",
                    "name": name,
                    "parameters": object_schema(params),
                    "strict": True,
                }
            )
    if memory:
        ret.append(
            {
                "type": "file_search",
                "vector_store_ids": [memory],
            }
        )
    return ret


def build_text(schema: dict | None) -> ResponseTextConfigParam | NotGiven:
    if not schema:
        return NOT_GIVEN
    return {
        "format": {
            "type": "json_schema",
            "name": "output",
            "schema": object_schema(schema),
            "strict": True,
        }
    }


def format_output(output: list[ResponseOutputItem], *, has_schema: bool):
    """Format the output list into a single message.

    Expects the output list to contain zero, one, or more text messages followed by
    at most one function call. If both text and function call are present, returns
    the function call. Otherwise, returns a combined text message."""
    text_output = []
    for i, item in enumerate(output):
        match item.type:
            case "function_call":
                assert i == len(output) - 1, "function call must be the last output"
                return {
                    "type": "function_call",
                    "name": item.name,
                    "args": json.loads(item.arguments),
                }
            case "message":
                text = item.content[0].text
                assert isinstance(text, str) and len(text) > 0, text
                text_output.append(text)

    if has_schema:
        assert len(text_output) == 1
        content = json.loads(text_output[0])
    else:
        content = "\n".join(text_output)

    return {
        "type": "message",
        "content": content,
    }


def new_response(
    messages,
    *,
    model,
    tools=None,
    schema=None,
    memory=None,
    timeout=30,
    on_function_call=None,
) -> dict:
    if tools is None:
        assert on_function_call is None, (
            "tools is None, so on_function_call must be None"
        )
    else:
        assert on_function_call is not None, (
            "tools is not None, so on_function_call must not be None"
        )

    extra = []
    while True:
        res = get_client().responses.create(
            model=model,
            input=messages + extra,
            tools=build_tools(tools, memory),
            parallel_tool_calls=False,
            text=build_text(schema),
            timeout=timeout,
            user="llmutil",  # improve cache hit rates
            store=False,
        )
        m = format_output(res.output, has_schema=bool(schema))
        match m:
            case {"type": "function_call", "name": name, "args": args}:
                ret = on_function_call(m)
                if not isinstance(ret, FunctionCallOutput):
                    return ret

                call_id = str(len(extra))
                extra.append(
                    {
                        "type": "function_call",
                        "call_id": call_id,
                        "name": name,
                        "arguments": json.dumps(args),
                    }
                )
                extra.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": ret.output
                        if isinstance(ret.output, str)
                        else json.dumps(ret.output),
                    }
                )
            case {"type": "message", "content": content}:
                return content
            case _:
                assert False
