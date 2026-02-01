import os
import time
import requests
from moviepy import VideoFileClip, concatenate_videoclips
from uploader import upload_to_drive

# Config
API_KEY = os.getenv("LEONARDO_API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")
PROMPT = "Cinematic drone shot of a futuristic cyberpunk city, 4k, neon lights, rain"

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def trigger_gen():
    url = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
    payload = {"prompt": PROMPT, "isPublic": False, "motionStrength": 5}
    res = requests.post(url, json=payload, headers=headers).json()
    return res['motionVideoGenerationJob']['generationId']

def wait_and_download(gen_id, name):
    url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
    while True:
        time.sleep(20)
        res = requests.get(url, headers=headers).json()
        job = res['generations_by_pk']
        if job['status'] == 'COMPLETE':
            video_url = job['generated_video_all_mp4_url']
            with open(name, "wb") as f:
                f.write(requests.get(video_url).content)
            return name
        print(f"Status for {name}: {job['status']}...")

# Main Loop
clip_names = []
for i in range(6): # 6 clips * 10s = 60s
    print(f"🎬 Generating Clip {i+1}/6")
    gid = trigger_gen()
    clip_names.append(wait_and_download(gid, f"temp_{i}.mp4"))

# Stitching
print("🧵 Stitching clips...")
clips = [VideoFileClip(c) for c in clip_names]
final_video = concatenate_videoclips(clips, method="compose")
final_video.write_videofile("final_video.mp4", codec="libx264")

# Upload
upload_to_drive("final_video.mp4", FOLDER_ID)
