from openai import OpenAI

_instance = None
default_model = "gpt-4.1"


def default_client():
    global _instance
    if _instance is None:
        _instance = OpenAI()
    return _instance
