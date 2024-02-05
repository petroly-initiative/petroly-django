from typing import Any
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """Reply with `true` or `false` based on whether the given message looks like spam, advertisement, or violation of academic integrity."""

USER_EX1 = """
message:
السلام عليكم ورحمة الله 
الي يبي مساعده يتفضل خاص 

بحوثات علميه 
حلول واجبات 
تكاليف 
اسايمنت 
عمل عروض بوربوينت 
برزنتيشن 
عمل سيرة ذاتية احترافية 
إعداد رسائل علمية 
عمل تقارير 
عمل مشاريع 
تصميم الانميشن 
حل دراسة حالة 
عمل خرائط مفاهيم

حل اختبارات 
انجليزي 
رياضيات 
لغة عربية 
مع ضمان الفل مارك"""

USER_EX2 = """
message:
السلام عليكم شباب 

هذا قروب خاص بحـلول مواد ( CS, SWE, COE) ،نسعى من خلاله لمساعدتكم و بيخدم عدد كبير من الطلاب وبيكون منفعه للجميع 🫂🤍. 

رابط القروب: 
https://forms.gle/VZ5AXMg2rokXnboA8

شكرًا لكم"""


def is_spam_or_ad(message):
    messages: Any = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": USER_EX2,
        },
        {
            "role": "assistant",
            "content": "false",
        },
        {
            "role": "user",
            "content": USER_EX1,
        },
        {
            "role": "assistant",
            "content": "true",
        },
        {
            "role": "user",
            "content": f"message:\n{message}",
        },
    ]
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
    )

    print(completion.choices[0].message)

    cont = str(completion.choices[0].message.content)
    is_spam = "true" in cont.lower()

    reason = ""
    if is_spam:
        messages.append(
            {
                "role": "user",
                "content": f"Explain why.",
            }
        )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )
        print(completion)
        reason = str(completion.choices[0].message.content)

    return is_spam, reason
