import os
import time
import requests
from uploader import upload_video_to_drive
from prompt_generator import (
    generate_initial_prompt,
    generate_continuation_prompt
)

# =========================
# CONFIG
# =========================
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")

if not LEONARDO_API_KEY:
    raise RuntimeError("❌ LEONARDO_API_KEY environment variable not set")

GENERATE_URL = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
STATUS_URL = "https://cloud.leonardo.ai/api/rest/v1/generations/{}"

HEADERS = {
    "authorization": f"Bearer {LEONARDO_API_KEY}",
    "accept": "application/json",
    "content-type": "application/json"
}

TOTAL_CLIPS = 7               # 7 × 4s ≈ 28s
MAX_WAIT_SECONDS = 20 * 60    # 20 minutes
POLL_INTERVAL = 25            # seconds (slightly faster)
MAX_STATUS_ERRORS = 5         # tolerate temporary API issues

OUTPUT_DIR = "ytauto"

# =========================
# HELPERS
# =========================
def ensure_output_folder():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Output folder ready: {OUTPUT_DIR}")


def safe_request(method, url, **kwargs):
    """Retry wrapper for transient network failures"""
    for attempt in range(3):
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except requests.RequestException as e:
            print(f"⚠️ Network error (attempt {attempt + 1}/3): {e}")
            time.sleep(2)
    return None


def extract_video_url(job: dict):
    """Safely extract Leonardo MP4 URL"""
    images = job.get("generated_images") or []
    for img in images:
        url = img.get("motionMP4URL")
        if isinstance(url, str) and url.endswith(".mp4"):
            return url
    return None


def generate_video(prompt: str):
    payload = {
        "prompt": prompt,
        "model": "MOTION2",
        "isPublic": False
    }

    print("🚀 Requesting video generation...")
    response = safe_request(
        "POST",
        GENERATE_URL,
        json=payload,
        headers=HEADERS,
        timeout=30
    )

    if not response or response.status_code != 200:
        print("❌ Generation request failed")
        return None

    try:
        gen_id = response.json()["motionVideoGenerationJob"]["generationId"]
    except Exception:
        print("❌ Invalid generation response:", response.text)
        return None

    print(f"🆔 Generation ID: {gen_id}")

    elapsed = 0
    status_errors = 0

    while elapsed < MAX_WAIT_SECONDS:
        status_response = safe_request(
            "GET",
            STATUS_URL.format(gen_id),
            headers=HEADERS,
            timeout=30
        )

        if not status_response or status_response.status_code != 200:
            status_errors += 1
            print(f"⚠️ Status check failed ({status_errors}/{MAX_STATUS_ERRORS})")

            if status_errors >= MAX_STATUS_ERRORS:
                print("❌ Too many status failures, aborting job")
                return None

            time.sleep(POLL_INTERVAL)
            continue

        status_errors = 0
        job = status_response.json().get("generations_by_pk") or {}
        status = job.get("status")

        print(f"🔄 Status: {status}")

        if status == "FAILED":
            print("❌ Generation FAILED")
            return None

        if status == "COMPLETE":
            video_url = extract_video_url(job)
            if video_url:
                print("🎥 Video URL resolved")
                return video_url

            print("❌ COMPLETE but no video URL found")
            print("🧪 Job payload:", job)
            return None

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    print("⏰ Generation timed out")
    return None


def download_video(video_url: str, filepath: str):
    print("📥 Downloading video...")
    response = safe_request(
        "GET",
        video_url,
        stream=True,
        timeout=60
    )

    if not response or response.status_code != 200:
        raise RuntimeError("❌ Failed to download video")

    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)


# =========================
# MAIN PIPELINE
# =========================
def main():
    ensure_output_folder()

    prompts = []

    print("🧠 Generating prompts...")
    first_prompt = generate_initial_prompt()
    prompts.append(first_prompt)

    for i in range(2, TOTAL_CLIPS + 1):
        prompts.append(
            generate_continuation_prompt(prompts[-1], i)
        )

    for idx, prompt in enumerate(prompts, start=1):
        print(f"\n🎬 Clip {idx}/{TOTAL_CLIPS}")

        try:
            video_url = generate_video(prompt)
            if not video_url:
                print("⚠️ Skipping clip")
                continue

            filename = os.path.join(OUTPUT_DIR, f"clip_{idx}.mp4")

            download_video(video_url, filename)
            upload_video_to_drive(filename)

            print(f"✅ Clip {idx} uploaded")

        except Exception as e:
            print(f"❌ Clip {idx} error:", e)

        finally:
            if os.path.exists(filename):
                os.remove(filename)
                print("🧹 Local cleanup complete")


if __name__ == "__main__":
    main()










# import os
# import time
# import requests
# from uploader import upload_video_to_drive

# LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
# PROMPT = "Hyper-realistic cinematic nature, 4k, drone shot of tropical island, sunset"

# HEADERS = {
#     "authorization": f"Bearer {LEONARDO_API_KEY}",
#     "accept": "application/json",
#     "content-type": "application/json"
# }

# GENERATE_URL = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
# STATUS_URL = "https://cloud.leonardo.ai/api/rest/v1/generations/{}"
# MAX_WAIT_SECONDS = 20 * 60   # 20 minutes
# POLL_INTERVAL = 30          # seconds



# def generate_video():
#     payload = {
#         "prompt": PROMPT,
#         "model": "MOTION2",
#         "isPublic": False
#     }

#     print("🚀 Requesting video generation...")
#     response = requests.post(
#         GENERATE_URL,
#         json=payload,
#         headers=HEADERS,
#         timeout=30
#     )

#     if response.status_code != 200:
#         print("❌ Generation request failed:", response.text)
#         return None

#     gen_id = response.json()["motionVideoGenerationJob"]["generationId"]
#     print(f"🆔 Generation ID: {gen_id}")

#     elapsed = 0

#     while elapsed < MAX_WAIT_SECONDS:
#         time.sleep(POLL_INTERVAL)
#         elapsed += POLL_INTERVAL

#         status_response = requests.get(
#             STATUS_URL.format(gen_id),
#             headers=HEADERS,
#             timeout=30
#         )

#         if status_response.status_code != 200:
#             print("⚠️ Status check failed, retrying...")
#             continue

#         job = status_response.json().get("generations_by_pk", {})
#         status = job.get("status")
#         print(f"🔄 Status: {status}")

#         if status == "FAILED":
#             print("❌ Generation failed")
#             return None

#         if status == "COMPLETE":
#             print("✅ Generation COMPLETE")

#             # ✅ CORRECT location for video URL (your account)
#             images = job.get("generated_images", [])
#             if images:
#                 video_url = images[0].get("motionMP4URL")
#                 if video_url:
#                     print("🎥 Video URL found (motionMP4URL)")
#                     return video_url

#             # 🔁 Fallback (future-proof)
#             for value in job.values():
#                 if isinstance(value, dict):
#                     for v in value.values():
#                         if isinstance(v, str) and v.endswith(".mp4"):
#                             print("🎥 Video URL found via fallback scan")
#                             return v

#             print("❌ COMPLETE but no video URL found")
#             return None

#     print("⏰ Generation timed out")
#     return None


# def download_video(video_url, filename):
#     print("📥 Downloading video...")
#     with requests.get(video_url, stream=True, timeout=60) as r:
#         r.raise_for_status()
#         with open(filename, "wb") as f:
#             for chunk in r.iter_content(chunk_size=1024 * 1024):
#                 if chunk:
#                     f.write(chunk)


# def main():
#     video_url = generate_video()
#     if not video_url:
#         return

#     filename = "final_video.mp4"

#     try:
#         download_video(video_url, filename)
#         upload_video_to_drive(filename)
#         print("✨ Video uploaded to Drive successfully!")

#     except Exception as e:
#         print("❌ Pipeline error:", e)

#     finally:
#         if os.path.exists(filename):
#             os.remove(filename)
#             print("🧹 Local file cleaned up")


# if __name__ == "__main__":
#     main()
