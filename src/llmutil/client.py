from openai import OpenAI

_instance = None


def default_client():
    global _instance
    if _instance is None:
        _instance = OpenAI()
    return _instance
