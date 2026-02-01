import os
import requests
import time
from moviepy import VideoFileClip, concatenate_videoclips
from uploader import upload_video_to_drive

# Config
API_KEY = os.getenv("LEONARDO_API_KEY")
PROMPT = "Hyper-realistic cinematic nature, 4k, drone shot of tropical island, sunset"
headers = {"authorization": f"Bearer {API_KEY}", "accept": "application/json", "content-type": "application/json"}

def generate_clip(index):
    url = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
    payload = {"prompt": f"{PROMPT}, angle {index}", "model": "MOTION2", "isPublic": False}
    
    response = requests.post(url, json=payload, headers=headers)
    res = response.json()
    
    if 'motionVideoGenerationJob' not in res:
        print(f"❌ API Error: {res}")
        return None
        
    gen_id = res['motionVideoGenerationJob']['generationId']
    print(f"⏳ Processing Test Clip (ID: {gen_id})...")

    # Poll for completion (Max 10 mins)
    for _ in range(20):
        time.sleep(30)
        status_res = requests.get(f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}", headers=headers).json()
        job = status_res.get('generations_by_pk', {})
        status = job.get('status')
        print(f"   Status: {status}...")
        
        if status == 'COMPLETE':
            return job.get('generated_video_all_mp4_url')
        elif status == 'FAILED':
            return None
    return None

def main():
    clips = []
    clip_filenames = []
    
    # TEST MODE: Only range(1) to generate a single video
    for i in range(1):
        video_url = generate_clip(i)
        if video_url:
            filename = f"test_clip_{i}.mp4"
            print(f"📥 Downloading clip from Leonardo...")
            video_data = requests.get(video_url).content
            with open(filename, "wb") as f:
                f.write(video_data)
            
            clips.append(VideoFileClip(filename))
            clip_filenames.append(filename)
            print(f"✅ Test Clip {i+1} ready.")
        
    if clips:
        print("🧵 Processing video for upload...")
        # Even for 1 clip, we run it through MoviePy to test the codec/render
        final_video = concatenate_videoclips(clips, method="compose")
        output_name = f"test_upload_{int(time.time())}.mp4"
        final_video.write_videofile(output_name, codec="libx264")
        
        # Close to release file lock
        for c in clips: c.close()
        
        print("☁️ Triggering Drive Upload...")
        upload_video_to_drive(output_name)
        
        # Cleanup
        os.remove(output_name)
        for f in clip_filenames: os.remove(f)
        print("✨ Test Finished Successfully!")
    else:
        print("❌ Test failed: No clips were generated.")

if __name__ == "__main__":
    main()
