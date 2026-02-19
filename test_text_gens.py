import requests
import json
import os

CLOUDFLARE_ID = "21ec370636d743551762a48bf196fefc"
CLOUDFLARE_TOKEN = "-XsjDrsl-z0Eo7oZnqTBwCmOYYmUTRoCa780-vXV"

def test_cloudflare_llama():
    print("\n--- Testing Cloudflare Llama 3 ---")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ID}/ai/run/@cf/meta/llama-3-8b-instruct"
    headers = {"Authorization": f"Bearer {CLOUDFLARE_TOKEN}"}
    payload = {"messages": [{"role": "user", "content": "Tell me a short joke about AI in Russian."}]}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Response: {r.json()['result']['response']}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_pollinations_text():
    print("\n--- Testing Pollinations Text (No Key) ---")
    url = "https://text.pollinations.ai/"
    payload = {
        "messages": [
            {"role": "system", "content": "You are a funny Russian copywriter."},
            {"role": "user", "content": "Напиши смешной концепт для картинки 'Кот-хакер'."}
        ],
        "model": "openai", # Pollinations often proxies to open models
        "seed": 42
    }
    try:
        # Pollinations text API usually works via GET or POST plain text/json
        # Let's try the direct endpoint usually used:
        resp = requests.get(f"https://text.pollinations.ai/Напиши смешной концепт для картинки 'Кот-хакер'?model=openai")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}...")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_cloudflare_llama()
    test_pollinations_text()
