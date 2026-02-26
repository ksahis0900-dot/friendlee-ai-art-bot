"""
Test script: Grok Imagine vs Ideogram v3 TURBO quality comparison
Sends both images to Telegram channel
"""
import os, requests, json, time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

KIE_KEY    = os.environ.get('KIE_KEY')
BOT_TOKEN  = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

KIE_CREATE  = "https://api.kie.ai/api/v1/jobs/createTask"
KIE_POLL    = "https://api.kie.ai/api/v1/jobs/recordInfo"
TG_PHOTO    = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

HEADERS = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}

# ─── Промпт для сравнения ───────────────────────────────────────────────────
PROMPT = (
    "A futuristic medieval knight fused with bioluminescent deep-sea jellyfish, "
    "armor made of crystallized coral and glowing tentacles, standing in a baroque cathedral "
    "half-submerged underwater, shafts of ethereal teal light piercing through stained glass, "
    "hyperrealistic, cinematic composition, 8K"
)


def create_task(model: str, input_payload: dict) -> Optional[str]:
    payload = {"model": model, "input": input_payload}
    try:
        r = requests.post(KIE_CREATE, json=payload, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            data = r.json()
            d = data.get('data', {})
            task_id = (d.get('taskId') or d.get('recordId') or d.get('id')
                       if isinstance(d, dict) else None)
            if task_id:
                print(f"  ✅ Task created: {task_id}")
                return task_id
            print(f"  ⚠️ No taskId in response: {str(data)[:200]}")
        else:
            print(f"  ⚠️ HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠️ Exception: {e}")
    return None


def poll_task(task_id: str, timeout_s: int = 180) -> Optional[str]:
    deadline = time.time() + timeout_s
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        time.sleep(8)
        try:
            pr = requests.get(f"{KIE_POLL}?taskId={task_id}", headers=HEADERS, timeout=30)
            if pr.status_code == 200:
                p_res = pr.json()
                s_data = p_res.get('data', {})
                if not isinstance(s_data, dict):
                    s_data = {}
                fail_code = s_data.get('failCode')
                if fail_code and str(fail_code) not in ['0', 'None', '']:
                    print(f"  ❌ failCode={fail_code}")
                    return None
                res_json_str = s_data.get('resultJson', '')
                if res_json_str:
                    try:
                        res_obj = json.loads(res_json_str)
                        urls = res_obj.get('resultUrls', [])
                        if urls:
                            print(f"  ✅ Image ready (attempt {attempt}): {urls[0]}")
                            return urls[0]
                    except Exception:
                        pass
                state = s_data.get('state', '')
                if state in ('fail', 'failed', 'error'):
                    print(f"  ❌ state={state}")
                    return None
                print(f"  ⏳ [{attempt}] state={state or '?'}, waiting...")
        except Exception as e:
            print(f"  ⚠️ Poll exception: {e}")
    print(f"  ⏱️ Timeout after {timeout_s}s")
    return None


def send_to_tg(image_url: str, caption: str):
    try:
        r = requests.post(TG_PHOTO, json={
            "chat_id": CHANNEL_ID,
            "photo": image_url,
            "caption": caption,
            "parse_mode": "HTML"
        }, timeout=30)
        if r.status_code == 200:
            print("  📤 Sent to Telegram!")
        else:
            print(f"  ⚠️ TG error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠️ TG exception: {e}")


def test_model(name: str, model_id: str, input_payload: dict):
    print(f"\n{'='*60}")
    print(f"🎨 Testing: {name}")
    print(f"{'='*60}")
    task_id = create_task(model_id, input_payload)
    if not task_id:
        print(f"  ❌ Failed to create task for {name}")
        return
    image_url = poll_task(task_id)
    if not image_url:
        print(f"  ❌ Failed to get image from {name}")
        return
    caption = (
        f"🧪 <b>Model test: {name}</b>\n\n"
        f"<i>{PROMPT[:120]}...</i>\n\n"
        f"#ModelTest #AIArt @fRieNDLee34"
    )
    send_to_tg(image_url, caption)


if __name__ == "__main__":
    print("🚀 Starting model comparison test...\n")
    print(f"Prompt: {PROMPT[:80]}...\n")

    # Test 1: Grok Imagine
    test_model(
        name="Grok Imagine",
        model_id="grok-imagine/text-to-image",
        input_payload={"prompt": PROMPT, "aspect_ratio": "1:1"}
    )

    # Test 2: Ideogram v3 TURBO
    test_model(
        name="Ideogram v3 TURBO",
        model_id="ideogram/v3-text-to-image",
        input_payload={
            "prompt": PROMPT,
            "rendering_speed": "TURBO",
            "style": "AUTO",
            "image_size": "square_hd",
            "num_images": "1"
        }
    )

    print("\n✅ Test complete!")
