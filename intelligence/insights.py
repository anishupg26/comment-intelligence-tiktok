from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

def generate_cluster_insight(cluster_comments):

    prompt = f"""
You are an AI product analyst for TikTok creators.

Given these comments:

{cluster_comments}

Return ONLY a valid JSON object with:
- theme (short phrase)
- classification (choose exactly ONE from: Request, Confusion, Praise, Skepticism, Noise)
- insight (strategic meaning)
- suggested_action (specific creator action)
- risk_flag (or "None")

Return strictly one JSON object. No markdown. No explanation.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    # Extract first valid JSON object safely
    start = content.find("{")
    brace_count = 0
    json_str = ""

    for char in content[start:]:
        if char == "{":
            brace_count += 1
        if char == "}":
            brace_count -= 1

        json_str += char

        if brace_count == 0 and json_str.strip():
            break

    return json.loads(json_str)

