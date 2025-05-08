import openai

from llmutil import gen_schema, gen_str

client = openai.OpenAI()

res = client.responses.create(
    model="gpt-4.1-mini",
    input="normalize this address: 1 hacker way, menlo park, california",
    text=gen_schema(
        street=gen_str("Street, use number and street name"),
        city=gen_str("City, capitalized"),
        state=gen_str("State, use 2 letter abbreviation"),
    ),
)

# {"street":"1 Hacker Way","city":"Menlo Park","state":"CA"}
print(res.output_text)
