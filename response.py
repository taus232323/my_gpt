import g4f

def get_gpt4_response(messages: list) -> str:
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=messages,
)
    print(response)
    print(len(response))
    return response

messages = []
while True:
    messages.append({"role": "user", "content": input()})
    messages.append({"role": "assistant", "content": get_gpt4_response(messages=messages)})
