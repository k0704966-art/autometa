import os
import datetime
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🗓️ Day-wise content rotation
DAY_ROTATION = {
    "Monday": "facts_explainer",
    "Tuesday": "did_you_know",
    "Wednesday": "myth_vs_reality",
    "Thursday": "poll_opinion",
    "Friday": "listicle",
    "Saturday": "curiosity_loop",
    "Sunday": "light_recap"
}


def _get_today_style():
    """Returns today's content style based on weekday"""
    today = datetime.datetime.now().strftime("%A")
    return DAY_ROTATION.get(today, "cinematic_story")


# 🧠 1️⃣ INITIAL PROMPT GENERATOR
def generate_initial_prompt():
    """
    Generates the FIRST cinematic video prompt
    based on day-wise rotation.
    """

    style = _get_today_style()

    model = genai.GenerativeModel("gemini-1.5-flash")

    instruction = f"""
Generate ONE cinematic AI video prompt.

Content Style: {style}

Visual Rules:
- Hyper-realistic
- Cinematic lighting
- 4K quality
- Smooth camera motion
- Short 4-second visual moment

Creative Rules:
- No quotes
- No explanations
- One single paragraph
- No text overlays
- No narration cues
- YouTube-ready

Theme Ideas:
Nature, travel, futuristic worlds, aerial views, epic landscapes

Goal:
This is the FIRST clip of a longer cinematic sequence.
"""

    response = model.generate_content(instruction)
    prompt = response.text.strip()

    print("🧠 Initial Gemini Prompt:", prompt)
    return prompt


# 🔁 2️⃣ CONTINUATION PROMPT GENERATOR
def generate_continuation_prompt(previous_prompt, clip_index):
    """
    Generates a FOLLOW-UP prompt that continues the same scene
    while evolving visuals slightly.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")

    instruction = f"""
You are continuing a cinematic video sequence.

Previous Scene Prompt:
{previous_prompt}

Task:
Generate the NEXT 4-second cinematic prompt.

Rules:
- Must feel like the SAME world and scene
- Advance time, camera angle, or motion slightly
- Introduce subtle variation (lighting, movement, perspective)
- Do NOT repeat the same description
- No quotes
- No explanations
- One paragraph only
- Cinematic, hyper-realistic, smooth motion
- No text, no narration

This is clip number {clip_index} in a continuous 30-second video.
"""

    response = model.generate_content(instruction)
    prompt = response.text.strip()

    print(f"🧠 Continuation Prompt {clip_index}:", prompt)
    return prompt
