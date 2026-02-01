import os
import time
import requests
from uploader import upload_to_drive

# Config
API_KEY = os.getenv("LEONARDO_API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")
PROMPT = "A cinematic close-up of a high-tech robot eye blinking, 4k, neon reflections"

headers = {
    "Authorization": f"Bearer {API_KEY}", 
    "Content-Type": "application/json",
    "accept": "application/json"
}

def wait_for_video(gen_id):
    url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
    print(f"⏳ Monitoring Video Generation (ID: {gen_id})")
    
    attempts = 0
    while attempts < 20:  # Max 10 minutes (20 * 30s)
        time.sleep(30)
        attempts += 1
        
        try:
            response = requests.get(url, headers=headers)
            res = response.json()
            job = res.get('generations_by_pk', {})
            status = job.get('status')
            
            print(f"   [Attempt {attempts}] Current Status: {status}")
            
            if status == 'COMPLETE':
                video_url = job.get('generated_video_all_mp4_url')
                if video_url:
                    print("✅ Video is ready!")
                    return video_url
            elif status == 'FAILED':
                print("❌ Leonardo reported a generation failure.")
                return None
        except Exception as e:
            print(f"⚠️ Polling error: {e}")
            
    print("❌ Timeout reached.")
    return None

# --- Main Logic ---
print("🚀 STEP 1: TRIGGERING VIDEO")
url = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
payload = {"prompt": PROMPT, "isPublic": False, "model": "MOTION2"}

response = requests.post(url, json=payload, headers=headers)
if response.status_code == 200:
    gen_id = response.json()['motionVideoGenerationJob']['generationId']
    
    # STEP 2: WAIT
    video_link = wait_for_video(gen_id)
    
    if video_link:
        # STEP 3: DOWNLOAD
        print("💾 Downloading file...")
        video_data = requests.get(video_link).content
        with open("test_video.mp4", "wb") as f:
            f.write(video_data)
            
        # STEP 4: UPLOAD
        print("☁️ Uploading to Google Drive...")
        try:
            upload_to_drive("test_video.mp4", FOLDER_ID)
            print("🎉 ALL DONE! Check your Drive folder.")
        except Exception as e:
            print(f"❌ Upload failed: {e}")
else:
    print(f"❌ API Trigger Failed: {response.text}")


# api check cost money
# import os
# import time
# import requests

# # Config
# API_KEY = os.getenv("LEONARDO_API_KEY")
# PROMPT = "A cinematic close-up of a high-tech robot eye blinking, 4k, neon reflections"

# headers = {
#     "Authorization": f"Bearer {API_KEY}", 
#     "Content-Type": "application/json",
#     "accept": "application/json"
# }

# print("🧪 STEP 1: TEST API TRIGGER")
# url = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
# payload = {"prompt": PROMPT, "isPublic": False, "model": "MOTION2"}

# try:
#     response = requests.post(url, json=payload, headers=headers)
#     print(f"DEBUG Status Code: {response.status_code}")
#     res = response.json()
#     print(f"DEBUG Response Body: {res}")
# except Exception as e:
#     print(f"❌ Failed to even talk to the API: {e}")

# If we get here and see the Response Body, the API is working!















# import os
# import time
# import requests
# # MoviePy v2.0+ specific imports
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from moviepy.video.compositing.concatenate import concatenate_videoclips
# from uploader import upload_to_drive

# # Config
# API_KEY = os.getenv("LEONARDO_API_KEY")
# FOLDER_ID = os.getenv("FOLDER_ID")
# PROMPT = "Cinematic drone shot of a futuristic cyberpunk city, 4k, neon lights, rain"

# headers = {
#     "Authorization": f"Bearer {API_KEY}", 
#     "Content-Type": "application/json",
#     "accept": "application/json"
# }

# def trigger_gen():
#     url = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
#     payload = {
#         "prompt": PROMPT, 
#         "isPublic": False, 
#         "motionStrength": 5
#     }
#     print(f"🚀 Sending request to Leonardo AI...")
#     response = requests.post(url, json=payload, headers=headers)
#     res = response.json()
    
#     if 'motionVideoGenerationJob' not in res:
#         print(f"❌ Error from API: {res}")
#         return None
        
#     return res['motionVideoGenerationJob']['generationId']

# def wait_and_download(gen_id, name):
#     url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
#     print(f"⏳ Waiting for {name} to render...")
    
#     while True:
#         time.sleep(20)
#         response = requests.get(url, headers=headers)
#         res = response.json()
        
#         job = res.get('generations_by_pk')
#         if not job:
#             continue
            
#         status = job.get('status')
#         if status == 'COMPLETE':
#             video_url = job.get('generated_video_all_mp4_url')
#             print(f"✅ Downloading {name}...")
#             video_data = requests.get(video_url).content
#             with open(name, "wb") as f:
#                 f.write(video_data)
#             return name
#         elif status == 'FAILED':
#             print(f"❌ Generation failed for {name}")
#             return None
            
#         print(f"Current Status: {status}...")

# # --- Main Execution ---
# clip_names = []
# for i in range(6): # 6 clips * 10s = 60s
#     print(f"\n🎬 Starting Clip {i+1}/6")
#     gid = trigger_gen()
#     if gid:
#         file_path = wait_and_download(gid, f"temp_{i}.mp4")
#         if file_path:
#             clip_names.append(file_path)
#     time.sleep(5)

# if len(clip_names) > 0:
#     print("\n🧵 Stitching clips together...")
#     clips = [VideoFileClip(c) for c in clip_names]
    
#     # Concatenate the clips
#     final_video = concatenate_videoclips(clips, method="compose")
    
#     # Save the file
#     final_video.write_videofile("final_video.mp4", codec="libx264", audio=False)
    
#     # Cleanup memory
#     for c in clips:
#         c.close()

#     print("\n☁️ Starting upload to Google Drive...")
#     upload_to_drive("final_video.mp4", FOLDER_ID)
# else:
#     print("❌ No clips were generated.")
