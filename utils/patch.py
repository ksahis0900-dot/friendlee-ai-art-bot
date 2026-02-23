with open("main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
skip = False
for i, line in enumerate(lines):
    if line.startswith("def generate_video_kie(prompt, duration=5):"):
        skip = True
        out.append("""def generate_video_kie_and_poll(prompt, duration=5):
    if not KIE_KEY:
        return None

    headers = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}
    providers = [
        {"name": "veo3_fast", "create": "https://api.kie.ai/api/v1/veo/generate", "poll": "https://api.kie.ai/api/v1/veo/record-detail", "payload": {"model": "veo3_fast", "prompt": prompt, "aspectRatio": "16:9"}},
        {"name": "veo3", "create": "https://api.kie.ai/api/v1/veo/generate", "poll": "https://api.kie.ai/api/v1/veo/record-detail", "payload": {"model": "veo3", "prompt": prompt, "aspectRatio": "16:9"}},
        {"name": "runway", "create": "https://api.kie.ai/api/v1/runway/generate", "poll": "https://api.kie.ai/api/v1/runway/record-detail", "payload": {"prompt": prompt, "duration": duration, "quality": "1080p", "aspectRatio": "16:9"}}
    ]

    import time
    for p in providers:
        print(f"🎬 Kie.ai Video ({p['name']}) создание задачи...", flush=True)
        try:
            r = requests.post(p['create'], json=p['payload'], headers=headers, timeout=60)
            if r.status_code == 200:
                data = r.json()
                if data.get('code') not in [0, 200]:
                    print(f"      [{p['name']}] API Error {data.get('code')}: {data.get('msg')}", flush=True)
                    continue

                d = data.get('data') or {}
                task_id = d.get('taskId') or d.get('task_id') or d.get('id')
                if not task_id:
                    print(f"      [{p['name']}] Нет taskId: {str(data)[:200]}", flush=True)
                    continue

                print(f"✅ Задача создана ({p['name']})! Task ID: {task_id}", flush=True)
                # Поллинг
                for attempt in range(60):
                    time.sleep(15)
                    try:
                        pr = requests.get(f"{p['poll']}?taskId={task_id}", headers=headers, timeout=30)
                        if pr.status_code == 200:
                            pdata = pr.json()
                            if pdata.get('code') == 404:
                                print(f"   [{attempt+1}] 404 Задача не найдена...", flush=True)
                                continue
                            d2 = pdata.get('data') or {}
                            state = d2.get('state') or d2.get('status')
                            msg = d2.get('failMsg') or d2.get('msg') or d2.get('reason') or pdata.get('msg')

                            if attempt % 3 == 0 or state:
                                print(f"   [{attempt+1}/60] state={state} msg={msg}", flush=True)

                            if state == 'success':
                                vinfo = d2.get('videoInfo') or {}
                                vurl = vinfo.get('videoUrl') or d2.get('url') or d2.get('video_url')
                                if vurl:
                                    print(f"✅ ВИДЕО ГОТОВО: {vurl}", flush=True)
                                    return vurl
                                print(f"❌ Провал: success но нет URL", flush=True)
                                break 
                            elif state in ['fail', 'failed', 'error']:
                                print(f"❌ Провал ({p['name']}): {msg}", flush=True)
                                break
                    except Exception as e:
                        print(f"⚠️ Ошибка поллинга: {e}", flush=True)
            else:
                print(f"      [{p['name']}] HTTP {r.status_code} {r.text[:200]}", flush=True)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}", flush=True)

    print("❌ Видео-модели Kie.ai не сработали", flush=True)
    return None
""")
    if skip and line.startswith("# ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ"):
        skip = False
        out.append("# ─────────────────────────────────────────────\n")
        out.append(line)
    elif not skip:
        out.append(line)

with open("main.py", "w", encoding="utf-8") as f:
    f.writelines(out)
