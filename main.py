import os
import time
import requests
from uploader import upload_video_to_drive

LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
PROMPT = "Hyper-realistic cinematic nature, 4k, drone shot of tropical island, sunset"

HEADERS = {
    "authorization": f"Bearer {LEONARDO_API_KEY}",
    "accept": "application/json",
    "content-type": "application/json"
}

GENERATE_URL = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
STATUS_URL = "https://cloud.leonardo.ai/api/rest/v1/generations/{}"
MAX_WAIT_SECONDS = 20 * 60   # 20 minutes
POLL_INTERVAL = 30          # seconds



def generate_video():
    payload = {
        "prompt": PROMPT,
        "model": "MOTION2",
        "isPublic": False
    }

    print("🚀 Requesting video generation...")
    response = requests.post(
        GENERATE_URL,
        json=payload,
        headers=HEADERS,
        timeout=30
    )

    if response.status_code != 200:
        print("❌ Generation request failed:", response.text)
        return None

    gen_id = response.json()["motionVideoGenerationJob"]["generationId"]
    print(f"🆔 Generation ID: {gen_id}")

    elapsed = 0

    while elapsed < MAX_WAIT_SECONDS:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        status_response = requests.get(
            STATUS_URL.format(gen_id),
            headers=HEADERS,
            timeout=30
        )

        if status_response.status_code != 200:
            print("⚠️ Status check failed, retrying...")
            continue

        job = status_response.json().get("generations_by_pk", {})
        status = job.get("status")
        print(f"🔄 Status: {status}")

        if status == "FAILED":
            print("❌ Generation failed")
            return None

        if status == "COMPLETE":
            print("✅ Generation COMPLETE")

            # ✅ CORRECT location for video URL (your account)
            images = job.get("generated_images", [])
            if images:
                video_url = images[0].get("motionMP4URL")
                if video_url:
                    print("🎥 Video URL found (motionMP4URL)")
                    return video_url

            # 🔁 Fallback (future-proof)
            for value in job.values():
                if isinstance(value, dict):
                    for v in value.values():
                        if isinstance(v, str) and v.endswith(".mp4"):
                            print("🎥 Video URL found via fallback scan")
                            return v

            print("❌ COMPLETE but no video URL found")
            return None

    print("⏰ Generation timed out")
    return None


def download_video(video_url, filename):
    print("📥 Downloading video...")
    with requests.get(video_url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def main():
    video_url = generate_video()
    if not video_url:
        return

    filename = "final_video.mp4"

    try:
        download_video(video_url, filename)
        upload_video_to_drive(filename)
        print("✨ Video uploaded to Drive successfully!")

    except Exception as e:
        print("❌ Pipeline error:", e)

    finally:
        if os.path.exists(filename):
            os.remove(filename)
            print("🧹 Local file cleaned up")


if __name__ == "__main__":
    main()
