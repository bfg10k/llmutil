from llmutil import gen, gen_schema, gen_str

sysmsg = "You are a helpful assistant that can answer questions and help with tasks."

result = gen(
    sysmsg,
    "What is the capital of the Japan?",
    gen_schema(
        answer=gen_str("Name of the capital"),
    ),
)
# {'answer': 'Tokyo'}
print(result)

result = gen(
    sysmsg,
    "What is the longest river in the world? A: Nile, B: Amazon, C: Yangtze, D: Mississippi",
    gen_schema(
        answer=gen_str("Choice", enum=["A", "B", "C", "D"]),
    ),
)
# {'answer': 'A'}
print(result)


result = gen(
    sysmsg,
    "what are the pokemon types?",
    gen_schema(
        types=gen_str("Pokemon types", array=True),
    ),
)
# {'types': ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']}
print(result)
