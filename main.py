import os
import requests
import time
from uploader import upload_video_to_drive

# API Configuration
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")
PROMPT = "Hyper-realistic cinematic nature, 4k, drone shot of tropical island, sunset"
HEADERS = {
    "authorization": f"Bearer {LEONARDO_API_KEY}",
    "accept": "application/json",
    "content-type": "application/json"
}

def generate_video():
    url = "https://cloud.leonardo.ai/api/rest/v1/generations-text-to-video"
    payload = {
        "prompt": PROMPT,
        "model": "MOTION2",
        "isPublic": False
    }
    
    print("🚀 Requesting video from Leonardo AI...")
    response = requests.post(url, json=payload, headers=HEADERS)
    res = response.json()
    
    if 'motionVideoGenerationJob' not in res:
        print(f"❌ API Error: {res}")
        return None
        
    gen_id = res['motionVideoGenerationJob']['generationId']
    print(f"⏳ Generation ID: {gen_id}. Polling for completion...")

    for i in range(20):
        time.sleep(30)
        status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{gen_id}"
        status_res = requests.get(status_url, headers=HEADERS).json()
        
        # Accessing the generation data
        job = status_res.get('generations_by_pk', {})
        status = job.get('status')
        print(f"   [Check {i+1}] Status: {status}")
        
        if status == 'COMPLETE':
            # Check all possible URL locations in the response
            # 1. Check generated_videos list (Most common for newer API)
            videos = job.get('generated_videos', [])
            if videos and len(videos) > 0:
                return videos[0].get('url')
            
            # 2. Check motionVideoUrl field
            if job.get('motionVideoUrl'):
                return job.get('motionVideoUrl')
                
            # 3. Check legacy fields
            url = job.get('generated_video_all_mp4_url') or job.get('motionMP4URL')
            if url:
                return url

            # 4. Deep check into variations if it exists
            variations = job.get('motion_variations', [])
            if variations:
                return variations[0].get('url')

            print("⚠️ Status is COMPLETE but no URL found in standard fields.")
            print(f"DEBUG DATA: {job.keys()}") # Helps identify new fields
            return None
            
        elif status == 'FAILED':
            return None
            
    return None
    
def main():
    # Step 1: Generate
    video_url = generate_video()
    
    if video_url:
        filename = "final_video.mp4"
        
        # Step 2: Download
        print(f"📥 Downloading video from: {video_url[:50]}...")
        video_content = requests.get(video_url).content
        with open(filename, "wb") as f:
            f.write(video_content)
            
        # Step 3: Upload
        try:
            upload_video_to_drive(filename)
            print("✨ Final Video Uploaded Successfully!")
        except Exception as e:
            print(f"❌ Upload Error: {e}")
        finally:
            # Step 4: Cleanup
            if os.path.exists(filename):
                os.remove(filename)
    else:
        print("❌ Could not get a video URL.")

if __name__ == "__main__":
    main()
