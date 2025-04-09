import inspect
import json
from collections.abc import Callable

from openai import OpenAI

client = OpenAI()


def tool_def(fn):
    assert isinstance(fn, Callable)

    name = fn.__name__
    doc = fn.__doc__
    assert doc is not None
    params = list(inspect.signature(fn).parameters.keys())

    sysmsg = ""
    usrmsg = f"""generate a tool definition for this function.
name: {name}
docstring: {doc}
params: {params}"""

    text = {
        "format": {
            "type": "json_schema",
            "name": "tool_def",
            "schema": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "description of the tool",
                    },
                    "params": {
                        "type": "object",
                        "description": "parameters of the tool",
                        "properties": {
                            p: {
                                "type": "object",
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["string", "number"],
                                        "description": "type of the parameter, can only be string or number",
                                    },
                                    "enum": {
                                        "type": ["array", "null"],
                                        "items": {
                                            "type": "string",
                                        },
                                        "description": "optional, allowed values of the parameter, only applicable when type is string",
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "description of the parameter",
                                    },
                                },
                                "additionalProperties": False,
                                "required": ["type", "enum", "description"],
                            }
                            for p in params
                        },
                        "additionalProperties": False,
                        "required": params,
                    },
                },
                "required": ["description", "params"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
    result = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": sysmsg},
            {"role": "user", "content": usrmsg},
        ],
        text=text,
    )
    data = json.loads(result.output_text)

    output_params = {}
    for p in params:
        output_params[p] = {
            "type": data["params"][p]["type"],
            "description": data["params"][p]["description"],
        }
        if data["params"][p]["enum"] is not None:
            output_params[p]["enum"] = data["params"][p]["enum"]

    return {
        "type": "function",
        "name": name,
        "description": data["description"],
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": output_params,
            "required": params,
            "additionalProperties": False,
        },
    }
