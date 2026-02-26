"""
Test script: model quality comparison for Kie.ai image models
Sends generated images to Telegram channel.

Usage: python test_models.py [grok|ideogram|zimage|imagen4fast|flux2pro|all]
"""
import os, requests, json, time, sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

KIE_KEY    = os.environ.get('KIE_KEY')
BOT_TOKEN  = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

KIE_CREATE = "https://api.kie.ai/api/v1/jobs/createTask"
KIE_POLL   = "https://api.kie.ai/api/v1/jobs/recordInfo"
TG_PHOTO   = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
HEADERS    = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}

PROMPT = (
    "A futuristic medieval knight fused with bioluminescent deep-sea jellyfish, "
    "armor made of crystallized coral and glowing tentacles, standing in a baroque cathedral "
    "half-submerged underwater, shafts of ethereal teal light piercing through stained glass, "
    "hyperrealistic, cinematic composition, 8K"
)

# ─── Model configs ───────────────────────────────────────────────────────────
MODELS = {
    "ideogram": {
        "name": "Ideogram v3 TURBO",
        "model_id": "ideogram/v3-text-to-image",
        "input": {"prompt": PROMPT, "rendering_speed": "TURBO", "style": "AUTO",
                  "image_size": "square_hd", "num_images": "1"},
    },
    "grok": {
        "name": "Grok Imagine",
        "model_id": "grok-imagine/text-to-image",
        "input": {"prompt": PROMPT, "aspect_ratio": "1:1"},
    },
    "imagen4fast": {
        "name": "Google Imagen 4 Fast",
        "model_id": "google/imagen4-fast",
        "input": {"prompt": PROMPT, "aspect_ratio": "1:1"},
    },
    "flux2pro": {
        "name": "Flux 2 Pro",
        "model_id": "flux-2/pro-text-to-image",
        "input": {"prompt": PROMPT, "aspect_ratio": "1:1"},
    },
    "zimage": {
        "name": "z-image",
        "model_id": "z-image",
        "input": {"prompt": PROMPT, "aspect_ratio": "1:1"},
    },
}


def create_task(model_id: str, input_payload: dict) -> Optional[str]:
    try:
        r = requests.post(KIE_CREATE, json={"model": model_id, "input": input_payload},
                          headers=HEADERS, timeout=60)
        if r.status_code == 200:
            d = r.json().get('data', {})
            task_id = (d.get('taskId') or d.get('recordId') or d.get('id')) if isinstance(d, dict) else None
            if task_id:
                print(f"  ✅ Task created: {task_id}")
                return task_id
            print(f"  ⚠️ No taskId: {str(r.json())[:200]}")
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
                s_data = pr.json().get('data', {})
                if not isinstance(s_data, dict):
                    s_data = {}
                fail_code = s_data.get('failCode')
                if fail_code and str(fail_code) not in ('0', 'None', ''):
                    print(f"  ❌ failCode={fail_code}")
                    return None
                res_json_str = s_data.get('resultJson', '')
                if res_json_str:
                    urls = json.loads(res_json_str).get('resultUrls', [])
                    if urls:
                        print(f"  ✅ Image ready (attempt {attempt}): {urls[0]}")
                        return urls[0]
                state = s_data.get('state', '')
                if state in ('fail', 'failed', 'error'):
                    print(f"  ❌ state={state}")
                    return None
                print(f"  ⏳ [{attempt}] state={state or '?'}")
        except Exception as e:
            print(f"  ⚠️ Poll exception: {e}")
    print(f"  ⏱️ Timeout after {timeout_s}s")
    return None


def test_model(key: str):
    cfg = MODELS[key]
    print(f"\n{'='*55}\n🎨 {cfg['name']}\n{'='*55}")
    task_id = create_task(cfg['model_id'], cfg['input'])
    if not task_id:
        print(f"  ❌ Failed to create task")
        return
    image_url = poll_task(task_id)
    if not image_url:
        print(f"  ❌ No image received")
        return
    caption = (
        f"🧪 <b>Model test: {cfg['name']}</b>\n\n"
        f"<i>{PROMPT[:120]}...</i>\n\n"
        f"#ModelTest #AIArt @fRieNDLee34"
    )
    try:
        r = requests.post(TG_PHOTO, json={"chat_id": CHANNEL_ID, "photo": image_url,
                                          "caption": caption, "parse_mode": "HTML"}, timeout=30)
        print("  📤 Sent!" if r.status_code == 200 else f"  ⚠️ TG {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  ⚠️ TG exception: {e}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = list(MODELS.keys()) if mode == "all" else [mode]
    print(f"🚀 Model test (mode={mode})\nPrompt: {PROMPT[:70]}...\n")
    for key in targets:
        if key not in MODELS:
            print(f"⚠️ Unknown mode: {key}. Options: {list(MODELS.keys())}")
            continue
        test_model(key)
    print("\n✅ Done!")
