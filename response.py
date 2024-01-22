import g4f

def get_gpt4_response(question):
    response = g4f.ChatCompletion.create(
    model=g4f.models.gpt_4,
    messages=[{"role": "user", "content": question}],
)
    return response

# print(get_response("Можно ли вызывать синхронную фунцию в асихронном коде python?"))