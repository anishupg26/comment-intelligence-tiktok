from openai import OpenAI
from dotenv import load_dotenv
import os
import csv
import json

load_dotenv()

client = OpenAI()

prompt = """
Generate exactly 200 realistic TikTok comments under a video about sleep cycles and REM sleep.

Distribution:
- 60 comments requesting part 2 or more explanation
- 50 confused about a step
- 40 praising
- 30 skeptical ("cap", "source?", "this fake")
- 20 short noise comments ("lol", "bro", emojis, etc.)

Make them short, messy, informal, TikTok-style.

Return ONLY a valid JSON array of strings.
Do not include explanations.
Do not wrap in markdown.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.9
)

content = response.choices[0].message.content.strip()

# Attempt to safely extract JSON array
start = content.find("[")
end = content.rfind("]") + 1
json_content = content[start:end]

comments = json.loads(json_content)

with open("data/comments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["comment"])
    for comment in comments:
        writer.writerow([comment])

print(f"Generated {len(comments)} comments and saved to data/comments.csv")

