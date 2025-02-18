import json

from openai import OpenAI

MODEL = "gpt-4o"
client = OpenAI()


def chat(messages, model=MODEL, **kwargs):
    assert isinstance(messages, list) and len(messages) > 0
    assert isinstance(model, str)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
    return response.choices[0].message.content


def gen(sysmsg, usrmsg, response_format, model=MODEL, **kwargs):
    assert isinstance(sysmsg, str)
    assert isinstance(usrmsg, str)
    assert isinstance(response_format, dict)
    assert isinstance(model, str)

    messages = [
        {"role": "system", "content": sysmsg},
        {"role": "user", "content": usrmsg},
    ]
    response = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=response_format,
        **kwargs,
    )
    return json.loads(response.choices[0].message.content)
