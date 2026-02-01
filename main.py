import os
import time
import requests
# MoviePy v2.0+ specific imports
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from uploader import upload_to_drive

# Config
API_KEY = os.getenv("LEONARDO_API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")
PROMPT = "Cinematic drone shot of a futuristic cyberpunk city, 4k, neon lights, rain"

headers = {
    "Authorization": f"Bearer {API_KEY}", 
    "Content-Type": "application/json",
    "accept": "application/json"
}

def trigger_gen():
    url = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
    payload = {
        "prompt": PROMPT, 
        "isPublic": False, 
        "motionStrength": 5
    }
    print(f"🚀 Sending request to Leonardo AI...")
    response = requests.post(url, json=payload, headers=headers)
    res = response.json()
    
    if 'motionVideoGenerationJob' not in res:
        print(f"❌ Error from API: {res}")
        return None
        
    return res['motionVideoGenerationJob']['generationId']

def wait_and_download(gen_id, name):
    url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
    print(f"⏳ Waiting for {name} to render...")
    
    while True:
        time.sleep(20)
        response = requests.get(url, headers=headers)
        res = response.json()
        
        job = res.get('generations_by_pk')
        if not job:
            continue
            
        status = job.get('status')
        if status == 'COMPLETE':
            video_url = job.get('generated_video_all_mp4_url')
            print(f"✅ Downloading {name}...")
            video_data = requests.get(video_url).content
            with open(name, "wb") as f:
                f.write(video_data)
            return name
        elif status == 'FAILED':
            print(f"❌ Generation failed for {name}")
            return None
            
        print(f"Current Status: {status}...")

# --- Main Execution ---
clip_names = []
for i in range(6): # 6 clips * 10s = 60s
    print(f"\n🎬 Starting Clip {i+1}/6")
    gid = trigger_gen()
    if gid:
        file_path = wait_and_download(gid, f"temp_{i}.mp4")
        if file_path:
            clip_names.append(file_path)
    time.sleep(5)

if len(clip_names) > 0:
    print("\n🧵 Stitching clips together...")
    clips = [VideoFileClip(c) for c in clip_names]
    
    # Concatenate the clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Save the file
    final_video.write_videofile("final_video.mp4", codec="libx264", audio=False)
    
    # Cleanup memory
    for c in clips:
        c.close()

    print("\n☁️ Starting upload to Google Drive...")
    upload_to_drive("final_video.mp4", FOLDER_ID)
else:
    print("❌ No clips were generated.")
