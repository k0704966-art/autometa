import os
import datetime
from google import genai

# ✅ Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

DAY_ROTATION = {
    "Monday": "facts_explainer",
    "Tuesday": "did_you_know",
    "Wednesday": "myth_vs_reality",
    "Thursday": "poll_opinion",
    "Friday": "listicle",
    "Saturday": "curiosity_loop",
    "Sunday": "light_recap"
}

def _today_theme():
    today = datetime.datetime.utcnow().strftime("%A")
    return DAY_ROTATION.get(today, "cinematic_story")

def generate_initial_prompt():
    theme = _today_theme()

    instruction = f"""
Generate ONE cinematic AI video prompt.

Theme: {theme}
Style: hyper-realistic, cinematic, 4K, smooth camera motion
Topics: nature, travel, futuristic, epic aerial scenery

Rules:
- One paragraph
- No quotes
- No explanation
- YouTube-ready
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=instruction
    )

    prompt = response.text.strip()
    print("🧠 Gemini Initial Prompt:", prompt)
    return prompt


def generate_continuation_prompt(previous_prompt: str, part: int):
    instruction = f"""
Continue this cinematic video story.

Previous scene:
{previous_prompt}

Create PART {part}:
- Same environment & mood
- New camera angle or motion
- Visually different from previous
- Seamless continuation
- One paragraph only
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=instruction
    )

    prompt = response.text.strip()
    print(f"🧠 Gemini Prompt Part {part}:", prompt)
    return prompt
