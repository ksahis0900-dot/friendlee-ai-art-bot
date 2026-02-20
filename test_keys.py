import requests

GOOGLE_KEY = "AIzaSyDay7jyyQIJSBOoAJnTvpAFJ6IzfM0G58U"
SILICONFLOW_KEY = "sk-tagguskjmvgkvbhwhhiqtxybahzllhmugrnivjymenfcafgj"

def test_gemini():
    print("Testing Gemini...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_KEY}"
    payload = {"contents": [{"parts": [{"text": "Say test"}]}]}
    try:
        r = requests.post(url, json=payload, timeout=20)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_silicon():
    print("\nTesting SiliconFlow...")
    url = "https://api.siliconflow.cn/v1/images/generations"
    headers = {"Authorization": f"Bearer {SILICONFLOW_KEY}", "Content-Type": "application/json"}
    payload = {"model": "black-forest-labs/FLUX.1-schnell", "prompt": "test", "image_size": "1024x1024", "num_inference_steps": 4}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()
    test_silicon()
