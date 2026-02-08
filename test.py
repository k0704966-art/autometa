import os
import json
import datetime
from google import genai
from uploader import upload_file_to_drive  # must support overwrite

# =========================
# CONFIG
# =========================
OUTPUT_DIR = "ytauto"
PROMPT_FILE = os.path.join(OUTPUT_DIR, "prompts.json")
TOTAL_SCENES = 7

# =========================
# ENV CHECK
# =========================
if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("❌ GEMINI_API_KEY is missing")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# =========================
# THEME ROTATION
# =========================
DAY_ROTATION = {
    "Monday": "facts_explainer",
    "Tuesday": "did_you_know",
    "Wednesday": "myth_vs_reality",
    "Thursday": "poll_opinion",
    "Friday": "listicle",
    "Saturday": "curiosity_loop",
    "Sunday": "light_recap"
}

def today_theme():
    return DAY_ROTATION.get(
        datetime.datetime.utcnow().strftime("%A"),
        "cinematic_story"
    )

# =========================
# GEMINI (ONE CALL)
# =========================
def generate_scene_prompts():
    theme = today_theme()

    instruction = f"""
Generate {TOTAL_SCENES} cinematic AI video prompts
that together form ONE seamless story (~30 seconds total).

Theme: {theme}
Style: cinematic, hyper-realistic, 4K, smooth camera motion
Topics: nature, travel, futuristic, epic aerial scenery

Rules:
- Same environment & mood across all scenes
- Each scene uses a DIFFERENT camera angle or motion
- Each scene = ONE paragraph
- No numbering
- No quotes
- No explanations

Return ONLY valid JSON:

{{
  "scenes": [
    "scene text 1",
    "scene text 2",
    "scene text 3",
    "scene text 4",
    "scene text 5",
    "scene text 6",
    "scene text 7"
  ]
}}
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=instruction
    )

    text = response.candidates[0].content.parts[0].text
    data = json.loads(text)

    scenes = data.get("scenes", [])
    if len(scenes) != TOTAL_SCENES:
        raise RuntimeError("❌ Gemini did not return 7 scenes")

    return scenes

# =========================
# SAVE + DRIVE UPLOAD
# =========================
def save_and_upload(prompts):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    payload = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "scene_count": len(prompts),
        "scenes": prompts
    }

    # overwrite local file
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print("💾 prompts.json saved locally")

    # upload & overwrite in Drive
    upload_file_to_drive(PROMPT_FILE)
    print("☁️ prompts.json uploaded to Google Drive (overwrite)")

# =========================
# MAIN
# =========================
def main():
    print("🧠 Generating cinematic prompts (ONE Gemini call)...")
    prompts = generate_scene_prompts()

    for i, p in enumerate(prompts, 1):
        print(f"\n🎬 Scene {i}:\n{p}")

    save_and_upload(prompts)
    print("\n✅ FULL TEST SUCCESS")

if __name__ == "__main__":
    main()
