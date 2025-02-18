# llmutil

This library provides tools to generate structured output from the OpenAI API.

## What is Structured Output?

[Structured Output](https://platform.openai.com/docs/guides/structured-outputs) is the recommended method for getting formatted responses. It guarantees that outputs follow your defined schema, making it more reliable than previous methods like JSON mode, function calls, or tool use.

## How to Use

To use Structured Output, you need to define a schema. This library makes it easy with simple functions:

```python
sysmsg = "You are a helpful assistant that can answer questions and help with tasks."

result = gen(
    sysmsg,
    "What is the capital of Japan?",
    gen_schema(
        answer=gen_str("Name of the capital"),
    ),
)
# {'answer': 'Tokyo'}
```

