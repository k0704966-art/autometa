import os
import json
import datetime
from google import genai

# ---------- GEMINI ----------
if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("❌ GEMINI_API_KEY is missing")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------- PATH RESOLUTION ----------
def get_output_paths():
    # Preferred: Google Drive (Colab)
    drive_base = "/content/drive/MyDrive"

    if os.path.exists(drive_base):
        output_dir = os.path.join(drive_base, "ytauto")
    else:
        # Fallback: local / CI
        output_dir = "ytauto"

    os.makedirs(output_dir, exist_ok=True)
    return output_dir, os.path.join(output_dir, "prompts.json")


OUTPUT_DIR, PROMPT_FILE = get_output_paths()

# ---------- THEME ----------
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
    return DAY_ROTATION.get(
        datetime.datetime.utcnow().strftime("%A"),
        "cinematic_story"
    )

# ---------- PROMPT GENERATOR ----------
def generate_scene_prompts():
    theme = _today_theme()

    instruction = f"""
You are creating prompts for an AI cinematic video.

Goal:
- Total video length ≈ 30 seconds
- 7 short cinematic scenes (≈4–5 seconds each)
- SAME environment, SAME world, SAME mood
- Each scene must use a DIFFERENT camera angle or motion

Theme: {theme}
Style: cinematic, highly detailed, smooth camera motion
Topics: nature, travel, futuristic, epic aerial scenery

Rules:
- Return EXACTLY 7 prompts
- Each prompt = ONE paragraph
- No quotes
- No explanations
- Continuous cinematic flow
- Different camera motion every scene

Output format (JSON only):
[
  "scene 1 prompt",
  "scene 2 prompt",
  "scene 3 prompt",
  "scene 4 prompt",
  "scene 5 prompt",
  "scene 6 prompt",
  "scene 7 prompt"
]
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=instruction
    )

    if not response.candidates:
        raise RuntimeError("❌ Gemini returned no output")

    raw = response.candidates[0].content.parts[0].text.strip()

    try:
        prompts = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"❌ Invalid JSON from Gemini:\n{raw}")

    if not isinstance(prompts, list) or len(prompts) != 7:
        raise RuntimeError("❌ Gemini did not return exactly 7 prompts")

    # ---------- WRITE / OVERWRITE ----------
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "theme": theme,
                "scenes": prompts
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"✅ prompts.json written to: {PROMPT_FILE}")
    return prompts












# import os
# import datetime
# from google import genai

# if not os.getenv("GEMINI_API_KEY"):
#     raise RuntimeError("❌ GEMINI_API_KEY is missing")

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# DAY_ROTATION = {
#     "Monday": "facts_explainer",
#     "Tuesday": "did_you_know",
#     "Wednesday": "myth_vs_reality",
#     "Thursday": "poll_opinion",
#     "Friday": "listicle",
#     "Saturday": "curiosity_loop",
#     "Sunday": "light_recap"
# }

# def _today_theme():
#     today = datetime.datetime.utcnow().strftime("%A")
#     return DAY_ROTATION.get(today, "cinematic_story")

# def generate_initial_prompt():
#     theme = _today_theme()

#     instruction = f"""
# Generate ONE cinematic AI video prompt.

# Theme: {theme}
# Style: hyper-realistic, cinematic, 4K, smooth camera motion
# Topics: nature, travel, futuristic, epic aerial scenery

# Rules:
# - One paragraph
# - No quotes
# - No explanation
# - YouTube-ready
# """

#     response = client.models.generate_content(
#         model="gemini-3-flash-preview",
#         contents=instruction
#     )

#     prompt = response.text.strip()
#     print("🧠 Gemini Initial Prompt:", prompt)
#     return prompt


# def generate_continuation_prompt(previous_prompt: str, part: int):
#     instruction = f"""
# Continue this cinematic video story.

# Previous scene:
# {previous_prompt}

# Create PART {part}:
# - Same environment & mood
# - New camera angle or motion
# - Visually different
# - Seamless continuation
# - One paragraph only
# """

#     response = client.models.generate_content(
#         model="gemini-3-flash-preview",
#         contents=instruction
#     )

#     prompt = response.text.strip()
#     print(f"🧠 Gemini Prompt Part {part}:", prompt)
#     return prompt
