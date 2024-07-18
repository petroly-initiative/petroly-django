import re
from typing import Tuple

import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
)


SYSTEM_PROMPT = """You are tasked with determining whether a given message appears to be spam, an advertisement, or a violation of academic integrity. Your job is to analyze the content and respond with either 'true' or 'false'.

Here is the message to analyze:

<message>
{message}
</message>

Carefully read and consider the message above. You should evaluate it based on the following criteria:

1. Spam: Does the message contain unsolicited bulk messages, irrelevant or inappropriate content, or attempts to deceive the recipient?
2. Advertisement: Is the primary purpose of the message to promote a product, service, or brand?
3. Violation of academic integrity: Does the message offer or request services that would compromise academic honesty, such as writing essays, completing assignments, or cheating on exams?

Analyze the message thoroughly, considering its content, tone, and purpose. Then, provide your reasoning for your decision in <reasoning> tags. Your reasoning should be clear and concise, explaining why you believe the message does or does not fall into one of the categories mentioned above.

After providing your reasoning, give your final answer as either 'true' (if the message appears to be spam, an advertisement, or a violation of academic integrity) or 'false' (if it does not) in <answer> tags.

Remember, you must output either 'true' or 'false' as your final answer, with no additional text or explanation within the <answer> tags."""


def parse_claude_response(response_string) -> Tuple[str | None, str | None]:
    # Use regular expressions to extract content from tags
    reasoning_match = re.search(
        r"<reasoning>(.*?)</reasoning>", response_string, re.DOTALL
    )
    answer_match = re.search(r"<answer>(.*?)</answer>", response_string, re.DOTALL)

    # Extract the content if matches are found, otherwise return None
    reasoning = reasoning_match.group(1).strip() if reasoning_match else None
    answer = answer_match.group(1).strip() if answer_match else None

    return (reasoning, answer)


def is_spam_or_ad(message):
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT.format(message=message),
                    }
                ],
            }
        ],
    )

    print(message)

    reason, answer = parse_claude_response(message.content[0].text)

    if answer is not None:
        is_spam = True if "true" in answer.lower() else False
    else:
        is_spam = False

    return is_spam, reason
