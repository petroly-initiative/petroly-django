from openai import OpenAI

client = OpenAI()

system_prompt = """Reply with `yes` or `no` based on whether the quoted text looks like spam or unwanted ads."""

USER_EX1 = """```السلام عليكم ورحمة الله 
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
مع ضمان الفل مارك```"""

USER_EX2 = """السلام عليكم شباب 

هذا قروب خاص بحـلول مواد ( CS, SWE, COE) ،نسعى من خلاله لمساعدتكم و بيخدم عدد كبير من الطلاب وبيكون منفعه للجميع 🫂🤍. 

رابط القروب: 
https://forms.gle/VZ5AXMg2rokXnboA8

شكرًا لكم"""


def is_spam_or_ad(message):
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "Reply with `yes` or `no` based on whether the triple-backtick quoted text looks like spam or unwanted ads",
            },
            {
                "role": "user",
                "content": USER_EX2,
            },
            {
                "role": "assistant",
                "content": "no",
            },
            {
                "role": "user",
                "content": USER_EX1,
            },
            {
                "role": "assistant",
                "content": "yes",
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
