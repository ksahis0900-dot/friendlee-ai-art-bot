import requests
import time
import json

def test_craiyon(prompt):
    print(f"Testing Craiyon with prompt: {prompt}")
    url = "https://api.craiyon.com/v3"
    payload = {
        "prompt": prompt,
        "token": None,
        "version": "35s5hfwn9n78gb06"
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        print(f"Craiyon Status: {r.status_code}")
        if r.status_code == 200:
            print("Craiyon Success!")
            # Craiyon returns a list of images in webp base64
            # images = r.json()['images']
            return True
        else:
            print(f"Craiyon Error: {r.text[:200]}")
    except Exception as e:
        print(f"Craiyon Exception: {e}")
    return False

def test_pollinations_extra(model):
    print(f"Testing Pollinations Model: {model}")
    url = f"https://image.pollinations.ai/prompt/test?model={model}&width=512&height=512&nologo=true"
    try:
        r = requests.get(url, timeout=30)
        print(f"Pollinations {model} Status: {r.status_code}")
        if r.status_code == 200 and len(r.content) > 1000:
            print(f"Pollinations {model} Success!")
            return True
    except Exception as e:
        print(f"Pollinations {model} Exception: {e}")
    return False

if __name__ == "__main__":
    test_craiyon("cyberpunk city")
    test_pollinations_extra("flux-anime")
    test_pollinations_extra("flux-3d")
    test_pollinations_extra("any-dark")
