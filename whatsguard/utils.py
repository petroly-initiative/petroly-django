from openai import OpenAI

client = OpenAI()


def is_spam_or_ad(message):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Reply with `yes` or `no` based on whether the triple-backtick quoted text looks like spam or unwanted ads",
            },
            {
                "role": "user",
                "content": f"```{message}```",
            },
        ],
    )

    print(completion.choices[0].message)
    cont: str = completion.choices[0].message.content
    return "yes" in cont.lower()
