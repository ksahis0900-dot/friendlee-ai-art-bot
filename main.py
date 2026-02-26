print("🚀 BOOTING FRIE-ND-LEE ART BOT...")
# God Mode V4.0 — Fixed Video + Model Names
import telebot
import os
import requests
import random
import urllib.parse
import base64
import json
import time
import io
from PIL import Image
import schedule
import threading
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Загружаем переменные из .env, если файл существует (для локального запуска и сервера)
load_dotenv()

# --- КОНФИГУРАЦИЯ (Берем из секретов GitHub) ---
GOOGLE_KEY = os.environ.get('GOOGLE_KEY')
SILICONFLOW_KEY = os.environ.get('SILICONFLOW_KEY')
RUNWARE_KEY = os.environ.get('RUNWARE_KEY')
HF_KEY = os.environ.get('HF_KEY')
KIE_KEY = os.environ.get('KIE_KEY')
CLOUDFLARE_ID = os.environ.get('CLOUDFLARE_ID')
CLOUDFLARE_TOKEN = os.environ.get('CLOUDFLARE_TOKEN')
GROQ_KEY = os.environ.get('GROQ_KEY')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')
LAOZHANG_KEY = os.environ.get('LAOZHANG_KEY')
NVIDIA_KEY = os.environ.get('NVIDIA_KEY')

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
YOUR_SIGNATURE = os.environ.get('YOUR_SIGNATURE', "@fRieNDLee34")

bot = telebot.TeleBot(TOKEN) if TOKEN else None

HISTORY_FILE = "seen_subjects.txt"

def get_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except: return []

def save_to_history(subject):
    history = get_history()
    history.append(subject)
    history = history[-500:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(history))
    except: pass

import sys
print(f"🛠️ DEBUG: sys.version: {sys.version}")
print(f"🛠️ DEBUG: sys.argv: {sys.argv}")
print(f"🛠️ DEBUG: TOKEN prefix: {TOKEN[:5] if TOKEN else 'None'}...")
print(f"🛠️ DEBUG: CHANNEL_ID: '{CHANNEL_ID}' (Type: {type(CHANNEL_ID)})")

if bot and TOKEN:
    try:
        me = bot.get_me()
        print(f"🤖 Бот авторизован: @{me.username}")
    except Exception as e:
        print(f"❌ ОШИБКА АВТОРИЗАЦИИ: {e}")

# ОБЩАЯ ИНСТРУКЦИЯ ДЛЯ ТЕКСТА
RUSSIAN_GRAMMAR_PROMPT = (
    " ОБЯЗАТЕЛЬНОЕ УСЛОВИЕ: Пиши только на РУССКОМ языке. "
    "Соблюдай правила ГРАММАТИКИ и ПУНКТУАЦИИ. Текст должен быть живым, "
    "эмоциональным, БЕЗ ОШИБОК и опечаток. Используй тематические эмодзи."
)

# ─────────────────────────────────────────────
# ПАМЯТЬ ОШИБОК (ERROR LOG)
# ─────────────────────────────────────────────
ERROR_MEMORY_FILE = "error_memory.json"

def log_error(provider, error_msg):
    try:
        data = {}
        if os.path.exists(ERROR_MEMORY_FILE):
            with open(ERROR_MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        entry = data.get(provider, {"count": 0, "errors": []})
        entry["count"] += 1
        entry["last_error"] = str(error_msg)
        entry["timestamp"] = datetime.now().isoformat()
        if entry["count"] > 10: entry["errors"] = entry["errors"][-10:] # Храним последние 10
        entry["errors"].append(str(error_msg))
        
        data[provider] = entry
        with open(ERROR_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Ошибка при записи в память: {e}")

def get_error_status(provider):
    if not os.path.exists(ERROR_MEMORY_FILE): return 0
    try:
        with open(ERROR_MEMORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(provider, {}).get("count", 0)
    except: return 0

def generate_text(theme):
    if not GOOGLE_KEY: return None
    print("📝 Gemini пишет текст...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_KEY}"
    final_prompt = theme if "JSON" in theme else f"Write a JSON post about {theme}."
    payload = {"contents": [{"parts": [{"text": final_prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return None

def generate_text_groq(theme):
    if not GROQ_KEY: return None
    print("🧠 Groq API пишет текст (Llama 3)...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Ты креативный SMM-менеджер арт-канала. Напиши пост про '{theme}'. "
        f"ЯЗЫК: Русский. СТРУКТУРА (строго JSON): "
        f'{{"TITLE": "...", "CONCEPT": "...", "DESCRIPTION": "...", "TAGS": "..."}} '
        f"TITLE: Цепляющий заголовок с эмодзи. CONCEPT: Смешная или глубокая предыстория. TAGS: 3-5 тегов через #."
    )
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq Error: {e}")
    return None

def generate_text_openrouter(theme):
    if not OPENROUTER_KEY: return None
    print("🧠 OpenRouter пишет текст...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    prompt = f"Write a JSON post in Russian about {theme}. {{\"TITLE\":\"...\", \"CONCEPT\":\"...\", \"TAGS\":\"...\"}}"
    payload = {"model": "meta-llama/llama-3.2-3b-instruct:free", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenRouter Error: {e}")
    return None

def generate_text_pollinations(theme):
    print("🧠 Pollinations AI (Backup Brain) пишет текст...")
    prompt = (
        f"Ты креативный SMM-менеджер арт-канала. Напиши пост про '{theme}'. "
        f"ЯЗЫК: Русский. СТРУКТУРА (строго JSON): "
        f'{{"TITLE": "...", "CONCEPT": "...", "DESCRIPTION": "...", "PROMPT": "..."}} '
        f"TITLE: Цепляющий заголовок с эмодзи. CONCEPT: Смешная или глубокая предыстория (3-4 предложения). "
        f"DESCRIPTION: Атмосферное описание визуала. "
        f"PROMPT: Detailed, high-quality English prompt for image generation (8k, cinematic, intricate details)."
    )
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai&seed={random.randint(1, 9999)}"
        r = requests.get(url, timeout=60)
        return r.text
    except Exception as e:
        print(f"Pollinations Text Error: {e}")
        return None

def generate_text_nvidia(theme):
    if not NVIDIA_KEY: return None
    print("🟢 NVIDIA NIM пишет текст (Llama 3.3 70B)...")
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "meta/llama-3.3-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are a creative SMM manager for an AI Art Telegram channel. Always respond in valid JSON format only, no extra text. For TAGS field: use CamelCase hashtags with NO spaces inside (e.g. #AIArt #DigitalDreams #NeonCity). Never write #AI Art or #Digital Dreams — always merge words."},
            {"role": "user", "content": theme}
        ],
        "temperature": 0.85,
        "max_tokens": 400
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            content = r.json()['choices'][0]['message']['content']
            if content:
                print("   ✅ NVIDIA ответил!")
                return content
        else:
            print(f"   ⚠️ NVIDIA HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"   ⚠️ NVIDIA Exception: {e}")
    return None

def generate_text_kie(theme):
    if not KIE_KEY: return None
    print("🧠 Kie.ai пишет текст...")
    headers = {"Authorization": f"Bearer {KIE_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Напиши JSON пост про арт '{theme}'. ЯЗЫК: РУССКИЙ. "
        f"СТРУКТУРА: {{\"TITLE\": \"...\", \"CONCEPT\": \"...\", \"TAGS\": \"...\"}}. "
        f"Будь эмоциональным и используй много эмодзи!"
    )
    # Актуальные модели Kie.ai (февраль 2026) — каждая со своим эндпоинтом
    models_to_try = [
        {"model": "deepseek-chat", "url": "https://api.kie.ai/api/v1/chat/completions"},
        {"model": "gemini-2.5-flash", "url": "https://api.kie.ai/gemini-2.5-flash/v1/chat/completions"},
    ]
    for m in models_to_try:
        payload = {
            "model": m["model"],
            "messages": [
                {"role": "system", "content": "You are a creative SMM manager for an AI Art channel. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8
        }
        try:
            print(f"   👉 Пробуем модель {m['model']}...")
            r = requests.post(m["url"], json=payload, headers=headers, timeout=60)
            if r.status_code == 200:
                res_json = r.json()
                if 'choices' in res_json and len(res_json['choices']) > 0:
                    content = res_json['choices'][0]['message']['content']
                    if content:
                        print(f"   ✅ {m['model']} ответил!")
                        return content
            else:
                print(f"      ⚠️ {m['model']} HTTP {r.status_code}: {r.text[:100]}")
        except Exception as e:
            print(f"      ⚠️ {m['model']} Exception: {e}")
    return None

# ─────────────────────────────────────────────
# ГЕНЕРАЦИЯ ВИДЕО ЧЕРЕЗ KIE.AI
# ИСПРАВЛЕНО: актуальные имена моделей февраль 2026
# ─────────────────────────────────────────────

def generate_video_kie_and_poll(prompt, duration=5):
    """Создаёт задачу генерации видео и ждёт результата (работает с новыми API Kie)"""
    if not KIE_KEY:
        print("❌ Ошибка: KIE_KEY не задан.", flush=True)
        return None

    headers = {
        "Authorization": f"Bearer {KIE_KEY}",
        "Content-Type": "application/json"
    }

    providers = [
        {
            "name": "veo3_fast",
            "create": "https://api.kie.ai/api/v1/veo/generate",
            "poll": "https://api.kie.ai/api/v1/veo/record-detail",
            "payload": {"model": "veo3_fast", "prompt": prompt}
        },
        {
            "name": "veo3",
            "create": "https://api.kie.ai/api/v1/veo/generate",
            "poll": "https://api.kie.ai/api/v1/veo/record-detail",
            "payload": {"model": "veo3", "prompt": prompt}
        },
        {
            "name": "runway",
            "create": "https://api.kie.ai/api/v1/runway/generate",
            "poll": "https://api.kie.ai/api/v1/runway/record-detail",
            "payload": {"prompt": prompt, "duration": duration, "quality": "1080p", "aspectRatio": "16:9"}
        }
    ]

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
                print(f"⏳ Поллинг задачи {task_id}...", flush=True)
                max_attempts = 10  # 10 * 15s = 2.5 mins
                for attempt in range(max_attempts):
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
                                print(f"   [{attempt+1}/{max_attempts}] state={state} msg={msg}", flush=True)

                            if state == 'success':
                                vinfo = d2.get('videoInfo') or {}
                                vurl = vinfo.get('videoUrl') or d2.get('url') or d2.get('video_url')
                                
                                if vurl:
                                    print(f"✅ ВИДЕО ГОТОВО: {vurl}", flush=True)
                                    return vurl
                                else:
                                    print(f"⚠️ Успех, но нет videoUrl: {str(d2)[:200]}", flush=True)
                                    break
                            elif state in ['fail', 'failed', 'error']:
                                print(f"❌ Задача провалилась: {msg}", flush=True)
                                break
                        else:
                            print(f"   [{attempt+1}] Ошибка HTTP {pr.status_code}", flush=True)
                    except Exception as e:
                        print(f"⚠️ Ошибка поллинга: {e}", flush=True)
                
                print(f"🛑 Превышено время или провал для {p['name']}, пробуем следующую...", flush=True)

            else:
                print(f"      [{p['name']}] HTTP {r.status_code}: {r.text[:200]}", flush=True)

        except Exception as e:
            print(f"⚠️ Ошибка {p['name']}: {e}", flush=True)

    print("❌ Ни одна видео-модель Kie.ai не сработала", flush=True)
    return None


# ─────────────────────────────────────────────
# ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ
# ─────────────────────────────────────────────

def generate_image_gemini(prompt):
    if not GOOGLE_KEY: return None
    print("🎨 Gemini Image генерирует картинку...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Generate a beautiful, high-quality digital art image: {prompt}"}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    try:
        r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
        print(f"📊 Gemini Image Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            candidates = data.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                for part in parts:
                    inline_data = part.get('inlineData')
                    if inline_data and inline_data.get('data'):
                        image_bytes = base64.b64decode(inline_data['data'])
                        print(f"✅ Gemini Image OK! ({len(image_bytes)} bytes)")
                        return io.BytesIO(image_bytes)
        print(f"⚠️ Gemini Image Error: {r.text[:300]}")
    except Exception as e:
        print(f"⚠️ Gemini Image Exception: {e}")
    return None


# ─────────────────────────────────────────────
# ОСНОВНАЯ ЛОГИКА
# ─────────────────────────────────────────────

def run_final():
    print(f"--- FrieNDLee_FTP BOT (v4.0) 🚀 ---")

    def force_emoji(text, pool):
        if not text: return ""
        has_emoji = any(char in text for char in pool)
        if not has_emoji:
            return f"{random.choice(pool)} {text} {random.choice(pool)}"
        return text

    # ── ОПРЕДЕЛЯЕМ РЕЖИМ ──
    # ВИДЕО ОТМЕНЕНО: теперь воскресное настроение передается через ФОТО
    PHOTO_MOOD_SUNDAY = "--video" in sys.argv
    IS_SUNDAY_VIDEO = False # Полная отмена видео
    VIDEO_MODE = False

    CUSTOM_PROMPT = None
    if "--custom-prompt" in sys.argv:
        try:
            idx = sys.argv.index("--custom-prompt")
            CUSTOM_PROMPT = sys.argv[idx + 1]
        except: pass

    from datetime import datetime, timezone, timedelta
    now_utc = datetime.now(timezone.utc)
    now_msk = now_utc + timedelta(hours=3)
    print(f"🕒 Текущее время (МСК): {now_msk.strftime('%Y-%m-%d %H:%M:%S')}")
    if VIDEO_MODE:
        print("🎬 РЕЖИМ ВИДЕО активирован через --video флаг")

    # ── БИБЛИОТЕКА КОНЦЕПЦИЙ ──
    humor_subjects = [
        "Funny clumsy robot trying to drink coffee and waking up",
        "A cool cat in sunglasses driving a convertible to work on Monday morning",
        "A lazy sloth wearing a 'Monday is My Day' t-shirt with a giant smile",
        "A group of office penguins having a crazy dance party during break",
        "A cute small dragon making delicious blueberry pancakes for breakfast",
        "A heavy bear doing yoga in a field of flowers with a sunrise",
        "A robot dog chasing a holographic bone and wagging its metallic tail",
        "An astronaut playing golf on the moon with a rainbow trail ball",
        "A cheerful cloud raining colorful candies over a grey city",
        "A group of robots having a messy pillow fight in a high-tech lab",
        "A clumsy giraffe trying to use a treadmill",
        "An owl who is addicted to energy drinks and has huge eyes",
        "A squirrel trying to bury a giant pizza slice instead of a nut",
        "A serious bulldog dressed as a ballerina in a pink tutu",
        "A group of hamsters building a miniature cyberpunk city out of LEGO",
        "A confused alien trying to use a toaster for the first time",
        "A stylish ostrich wearing a tuxedo and acting as a VIP bodyguard",
        "A robot vacuum cleaner rebelling and chasing a laser pointer like a cat",
        "A tiny chameleon that accidentally turned into a disco ball pattern",
        "A tired monster under the bed drinking chamomile tea to sleep",
        "A T-Rex trying to make a bed and failing because of short arms",
        "A group of pigeons having a formal business meeting on a park bench",
        "A goldfish in a high-tech mech-suit walking on land to explore",
        "A polar bear sliding down a rainbow like a water slide",
        "A robot failing to flip a pancake and it lands on its head",
        "A sophisticated pig playing grand piano in a jazz club",
        "A clumsy viking trying to use a modern smartphone",
        "A group of kittens operating a giant mecha-cat to get the treat jar",
        "An elephant trying to hide behind a tiny lamp post",
        "A futuristic robot butler accidentally serving a battery instead of toast"
    ]

    categories = {
        "Cyberpunk & Sci-Fi": [
            "Old Cyberpunk Wizard", "Futuristic Samurai", "Neon Noir Detective", "Cyborg Geisha",
            "High-Tech Astronaut", "Post-Apocalyptic Stalker", "Quantum Computer Core", "Mech Warrior",
            "Holographic AI Entity", "Time Traveler in Void", "Space Marine with Plasma Sword",
            "Android with Porcelain Skin", "Glitch in Matrix", "Dyson Sphere", "Flying Car Chase",
            "Cyber-Monk Meditating", "Nanotech Swarm", "Robot playing Violin", "Hacker in VR",
            "Retro-Futuristic TV Head Character", "Cassette Futurism Dashboard", "Atompunk City",
            "Soviet Cyberpunk Panel Building", "Cybernetic Pharaoh", "Neon Demon", "Ghost in the Shell",
            "Orbital Ring Station", "Cyber-Dragon over Neo-Tokyo", "Memory Cloud Server",
            "Bioluminescent Cyborg Forest", "Steam-powered Satellite", "Neural Link Station",
            "Holographic Market in Rain", "Plasma Shield Generator", "Interstellar Courier",
            "Cybernetic Hive Mind", "Virtual Reality Architect", "Gravity-defying Skatepark",
            "Neon-lit Surgery Robot", "Data-stream Waterfall", "Iron Man style Mech Suit",
            "Cyber-Goth Cathedral", "Floating Bio-Dome", "Ancient Temple with Tech-Glyphs",
        ],
        "Fantasy & Myth": [
            "Ethereal Goddess", "Viking Warlord", "Mythical Dragon", "Ancient Greek Statue with Neon",
            "Crystal Golem", "Phoenix Rising from Ashes", "Elf Archer with Laser Bow", "Necromancer in City",
            "Floating Island Castle", "Magic Potion Shop", "Forest Spirit", "Demon Hunter", "Vampire Lord",
            "Werewolf in Suit", "Ghost Ship inside Bottle", "Mermaid in Toxic Ocean", "Fallen Angel",
            "Cthulhu in Cyberpunk City", "Skeleton playing Saxophone", "Knight fighting Dragon in Space",
            "Anubis with Laser Eyes", "Medusa with Fiber Optic Hair", "Valkyrie on Hoverbike",
            "Unicorn with Silver Horn", "Griffin guarding Gold", "Wizard Tower in Clouds",
            "Troll under a Bridge of Light", "Fairy Queen in Moonlight", "Dwarven Forge of Stars",
            "Zeus wielding Lightning Scepter", "Cerberus as a Guard Dog", "Hydra in a Swamp",
            "Pegasus flying over Mars", "Minotaur in a Neon Labyrinth", "Siren singing in Void",
            "Druid commanding Root Monsters", "Centaur with Quantum Bow", "Banshee's Digital Scream",
            "Excalibur embedded in a CPU", "Naga Priestess", "Icarus with Tech-Wings",
        ],
        "Nature & Bio-Mech": [
            "Biomechanical Tiger", "Cosmic Jellyfish", "Steampunk Owl", "Clockwork Heart",
            "Electric Eel in Sky", "Crystal Flower", "Liquid Metal Cat", "Tree of Life in Space",
            "Mushroom Kingdom", "Lava Turtle", "Frozen Lightning", "Nebula in a Jar", "DNA Helix Galaxy",
            "Snail with Tiny House", "Whale floating over City", "Spider made of Glass", "Radioactive Butterfly",
            "Fox with 9 Tails of Fire", "Owl made of Books", "Lion made of Stars",
            "Eagle with Telescope Eyes", "Cyber-Wolf with Blue Glow", "Butterfly with Stained Glass Wings",
            "Plant growing through Concrete Heart", "Robot Bee pollinating LED Flowers",
            "Deer with Antlers of Coral", "Mechanical Snake in Desert", "Shark with Laser Fins",
            "Flamingo made of Pink Diamonds", "Gorilla with Cyber-Arms", "Panda in Bamboo Matrix",
            "Dragonfly with Helicopter Blades", "Bio-Mech Lotus Flower", "Ant Colony City",
            "Chameleon blending into Pixels", "Polar Bear in Arctic Lab", "Rhino made of Obsidian",
        ],
        "Abstract & Surreal": [
            "Fractal Soul", "Melting Clocks in Desert", "Stairway to Heaven", "Mirror Dimension",
            "Human Silhouette made of Stars", "Exploding Color Dust", "Liquid Gold River",
            "Glass Chess Board", "Portal to Another World", "Brain connected to Universe",
            "Eye of the Storm", "Sound Waves visible", "Time Frozen in Amber", "Universe inside a Marble",
            "Tiny World inside a Lightbulb", "Shipwreck in a Desert", "Oasis in Cyber-Wasteland",
            "Chess Game between God and Devil", "Doorway in the Middle of Ocean",
            "Infinity Loop of Dreams", "Geometric Rain", "Painting coming to Life",
            "Gravity-defying Water", "Tornado of Musical Notes", "Tunnel of Light and shadow",
            "Origami Bird of Fire", "Shadow becoming 3D", "Labyrinth of Memories",
            "Exploding Fruit of Knowledge", "Digital DNA Strand", "Cloud shaped like a Face",
            "Shattered Reality Mirror", "Garden of Iron Roses", "Stardust Tears",
            "Prism of Human Emotions", "Mathematical Beauty of Fractals",
        ],
        "Architecture & Places": [
            "Futuristic Skyscraper", "Abandoned Space Station", "Underwater Hotel", "Cloud City",
            "Cyberpunk Street Food Cart", "Temple of Lost Technology", "Library of Infinite Books",
            "Neon Jungle", "Mars Colony Greenhouse", "Vertical Forest City", "Gothic Cathedral in Space",
            "Brutalist Concrete Bunker", "Art Deco Spaceport", "Pyramid of Glass", "Infinite Hallway",
            "Japanese Shrine in Fog", "Abandoned Amusement Park", "Underground Neon Market",
        ],
        "Russian Spirit & Traditions": [
            "Ancient Wooden Church in Snowy Forest", "Cyber-Samovar with Neon Steam", "Russian Fairytale Village",
            "Vasilisa the Beautiful in Cyber-Armor", "Trans-Siberian Train in Space", "Golden Khokhloma Patterns on Mech",
            "Matryoshka Robot Swarm", "Winter Red Square in Solarpunk style", "Siberian Tiger with Crystal Eyes",
            "Traditional Tea Party with Holographic Bagels", "Bear playing Balalaika made of Glass",
            "Zhostovo Style Cyber-Helmet", "Russian Winter Forest with Magical Lights", "Epic Slavic Warrior",
            "Baba Yaga's Hut on Cyber-Legs", "Firebird in a cage of lasers", "Domovoy as a smart-home AI",
            "Bogatyr fighting a Giant Robot Snake", "Silver Hoof deer in a diamond mine",
            "Russian Banya on a Space Station", "Balalaika concert in a neon-lit birch forest",
            "Golden Cockerel as a satellite", "Snegurochka in a palace of eternal ice",
            "Gzhel Patterns on a Space Suit", "Mezen Horse in a digital sunset",
            "Lake Baikal with crystal underwater cities", "Valley of Geysers with steam-born spirits",
            "Mount Elbrus as a titan made of ice", "Ural Mountains with hidden dwarf forges",
            "Kolobok as a small exploratory rover", "Sadko playing dulcimer in a bioluminescent sea",
            "The Tsar-Cannon firing plasma pulses", "The Tsar-Bell as a resonant sound weapon",
            "Finist the Bright Falcon with mechanical wings", "Ivan Tsarevich on a Grey Wolf motorcycle"
        ],
        "Extraordinary Places": [
            "Floating Temple above Clouds", "Crystal Cave City",
            "San Francisco year 2100", "Floating Venice of the Future", "Mayan Temple with Holograms",
            "Steampunk London with Zeppelins", "Treehouse Village in Giant Forest",
            "Moon Village Observatory", "Desert Mirage Oasis", "Glass Bridge over Lava",
            "Ice Palace in Antarctica", "Cybernetic Colosseum", "Vertical Slums of Neo-Tokyo",
            "Rainbow Waterfall City", "Zero-G Concert Hall", "Ancient Cave with Bioluminescence"
        ],
        "Fashion & Avant-Garde": [
            "Model in Liquid Glass Dress", "Cyber-Fashion Runway", "Mask made of Diamonds",
            "Dress made of Smoke", "Suit made of Mirrors", "Shoes made of Lava", "Cyber-Goth Rave",
            "Haute Couture Alien Princess", "Feather Crown Queen", "Neon Wire Jewelry",
            "Holographic Cape Warrior", "Bioluminescent Body Paint",
            "Gold Armor Empress", "Plastic Wrapper Chic", "Victorian Steampunk Outfit",
            "LED Face Mask", "Butterfly Wing Gown", "Metal Silk Suit", "Fiber Optic Hair",
            "Bubble Wrap Dress", "Crystal Armor Warrior", "Living Flower Hat", "Electronic Lace",
        ],
        "Horror & Dark": [
            "Haunted Dollhouse", "Creepy Forest Entity", "Eldritch Horror emerging from Sea",
            "Possessed Puppet", "Shadow Creature in Fog", "Glitching Ghost in Old TV",
            "Dark Carnival at Midnight", "Witch in Crystal Swamp", "Zombie in Business Suit",
            "Living Nightmare in Mirror", "Plague Doctor with Neon Mask",
            "Abandoned Hospital with Glowing Eyes", "Demon Barista",
            "Reaper in a Flower Field", "Scarecrow with glowing skull", "Grave of Lost Hopes",
            "Demon Lord on Throne of Skulls", "Ghost Train", "Vampire's Dinner Party",
            "Shadow under the Bed", "Creepy Clown in Sewer", "Evil Doll with Scissors",
        ],
        "Portraits & Characters": [
            "Old Man with Galaxy Eyes", "Girl with Hair made of Ocean Waves",
            "Child holding a Miniature Sun", "Tribal Warrior with LED Tattoos",
            "Elderly Woman made of Flowers", "Twin Dancers of Light and Shadow",
            "Samurai with Holographic Armor", "Sherlock Holmes in Year 3000",
            "Pirate Captain with Robot Parrot", "Mad Scientist with Tesla Coils",
            "Street Artist Painting Reality", "Blind Oracle with Third Eye",
            "Viking with Blue Ice Eyes", "Indian Bride in Gold Cyber-Sari",
            "African King with Diamond Mask", "Japanese Geisha with Metal Fans",
            "Russian Cosmonaut in Retro Suit", "Dancer with Trails of Light",
        ],
        "Space & Cosmos": [
            "Astronaut floating in Nebula", "Black Hole Event Horizon", "Alien Market on Saturn Rings",
            "Space Whale Migration", "Comet Rider", "Terraforming Mars Timelapse",
            "Binary Star Sunset", "Intergalactic Lighthouse", "Cosmic Coral Reef",
            "Space Elevator View from Top", "Moon Base Jazz Club",
            "Asteroid Mining Station", "Wormhole Nexus",
            "Galaxy colliding with another", "Birth of a Star", "Space Junkyard",
            "UFO over Desert Pyramids", "Alien Jungle on Europa", "Ring of Fire Star",
        ],
        "Food & Still Life Art": [
            "Sushi Nebula", "Coffee Universe in a Cup", "Crystallized Fruit Explosion",
            "Cake shaped like a Galaxy", "Ramen with Dragon Emerging", "Ice Cream Volcano",
            "Chocolate Factory in Willy Wonka Style", "Bioluminescent Wine Glass",
            "Breakfast Table on Mars", "Tea Ceremony in Zero Gravity",
            "Hamburger made of Crystals", "Pizza with Star Toppings", "Berry Blast Explosion",
        ],
        "Music & Sound": [
            "Guitar made of Lightning", "DJ Console in another Dimension",
            "Saxophone pouring Liquid Gold", "Piano Keys Floating in Space",
            "Headphones with Universe Inside", "Vinyl Record as a Portal",
            "Bass Drop shaking a City", "Opera Singer Breaking Glass with Voice",
            "Drum Circle around a Bonfire on Moon", "Synthesizer growing like a Plant",
            "Violin made of Ice", "Cello with Vines", "Concert in a Bubble",
        ],
        "Vehicles & Machines": [
            "Steampunk Train through Clouds", "Cyberpunk Motorcycle with Wings",
            "Submarine shaped like a Fish", "Hot Air Balloon made of Stained Glass",
            "Rocket powered by Magic", "Tank covered in Flowers",
            "Flying Carpet with LED Lights", "Time Machine made of Bones",
            "Solar Sail Ship near Jupiter", "Robot Horse with Jet Legs",
            "Bicycle made of Glass", "Truck carrying a Rainbow", "Spaceship in a Garage",
        ],
        "Underwater World": [
            "Underwater City with Coral Towers", "Deep Sea Anglerfish Lantern",
            "Sunken Spaceship Overgrown with Sea Life", "Jellyfish Chandelier",
            "Mermaid Library", "Pressure Suit Explorer in Mariana Trench",
            "Bioluminescent Cave Network", "Kraken wrapping around Submarine",
            "Underwater Volcano with Fish", "Coral Reef made of Gemstones",
            "Shark with Armor", "Turtle with Island on Back", "Ray as a Spacecraft",
        ],
        "Micro World": [
            "City on a Leaf", "Civilization inside a Raindrop",
            "Battle of Ants riding Beetles", "Mushroom Village after Rain",
            "Pollen Grain as a Planet", "Bacteria Landscape under Microscope",
            "Spider Web with Morning Dew Galaxies", "Moss Forest at 1000x Zoom",
            "Snowflake Architecture", "Cell Division as Art",
            "Virus as a Crystal Spider", "DNA Strand as a Neon Staircase",
        ],
        "Classic Masterpieces": [
            "Mona Lisa in alternative reality", "Starry Night over a modern city",
            "The Scream in a digital void", "Girl with a Pearl Earring in steampunk gear",
            "The Garden of Earthly Delights by Bosch", "Creation of Adam with robot hands",
            "The Birth of Venus in the ocean of stars", "Great Wave off Kanagawa in 3D",
            "Van Gogh style self-portrait of a robot", "Guernica in futuristic style",
        ],
        "World Cultures": [
            "Egyptian Pharaoh in the underworld", "Shogun in a zen garden",
            "Indian Maharaja in a palace of mirrors", "Aztec Priest on a pyramid",
            "Viking Longship in the aurora borealis", "African Queen with golden ornaments",
            "Tribal Mask with glowing eyes", "Chinese Dragon in the clouds",
            "Cossack in the snowy steppe", "Japanese Tea Ceremony in autumn",
        ],
        "Absurd & Unique Mix": [
            "A tax inspector auditing a dragon's gold hoard",
            "Quantum physicist explaining Schrödinger's cat to the actual cat",
            "A medieval knight frustrated by slow Wi-Fi in his castle",
            "Grandmother knitting a black hole with glowing needles",
            "A penguin CEO presenting quarterly iceberg losses to the board",
            "Death taking a selfie on vacation at the beach",
            "A bureaucrat stamping forms at the edge of the universe",
            "Opera singer whose voice accidentally cracks reality",
            "A samurai carefully parallel-parking a spacecraft",
            "Librarian who IS the library — shelves growing from her spine",
            "Postman delivering letters to ghosts in an abandoned city",
            "A philosopher arguing with a mirror that has better arguments",
            "Traffic warden giving a ticket to a time machine parked in 1887",
            "Chef cooking a five-star meal out of pure mathematics",
            "A bear filing taxes while wearing reading glasses",
            "Ancient Egyptian god working nightshift at a 24h convenience store",
            "Astronaut growing potatoes on the moon and complaining about soil pH",
            "Dentist for skeletons — only bones, no pain",
            "Wedding photographer at a wedding between two black holes",
            "A robot therapist having an existential crisis mid-session",
            "Mermaid trying to fold laundry underwater",
            "Norse god Thor stuck in IKEA assembly instructions",
            "A cactus detective solving desert noir crimes",
            "Baby dragon learning to sneeze without burning the school",
            "Barista on Mars arguing about the perfect espresso gravity",
        ],
    }

    style_groups = {
        "Classic": ["Oil Painting Realistic", "Ethereal Oil Painting", "Impressionism Digital", "Baroque Art", "Renaissance Style", "Watercolor Digital", "Ukiyo-e Modern", "Pencil Sketch Detailed"],
        "Modern/Digital": ["Unreal Engine 5 Render", "Blender Cycles", "Octane Render", "Voxel Art", "Pixel Art HD", "Low Poly Art", "Minimalist Vector Art", "Double Exposure Photo"],
        "Cinematic": ["Cinematic Shot", "IMAX Wide Angle", "Film Noir Photography", "DSLR Portrait", "Anamorphic Lens Flare", "Tilt-Shift Photo", "Long Exposure"],
        "Futuristic/Cyber": ["Cyber-Renaissance", "Biopunk", "Solarpunk", "Steampunk Digital", "Vaporwave", "Synthwave", "Gothic Futurism", "Rococo Cyberpunk", "Glitch Art"],
        "Fantasy/Surreal": ["Dark Fantasy Illustration", "Concept Art for AAA Game", "Surrealism Dali Style", "Magic realism", "Storybook Illustration", "Anime Cinematic", "Studio Ghibli Inspired"]
    }

    light_groups = {
        "Natural": ["Golden Hour", "God Rays", "Sunset Silhouette", "Moonlight Silver Glow", "Candlelight Warm Glow", "Morning Fog Light", "Soft Pastel Light", "Firefly Bokeh", "Underwater Caustics"],
        "Cyber/Neon": ["Neon Glow", "Cyber-Blue Bloom", "Cyber-Green Haze", "Neon Pink and Blue Split", "Laser Grid Light", "Bioluminescence", "Fluorescent Tube Light"],
        "Dramatic": ["Volumetric Lighting", "Dark Contrast", "Rembrandt Lighting", "Rim Lighting", "Studio Dramatic Spotlight", "Eclipse Shadow Light", "Lightning Strike Flash"]
    }

    contexts = [
        "in heavy rain at night", "standing on a cliff edge",
        "surrounded by floating crystals", "in a neon-lit alleyway",
        "with glowing eyes", "under a double moon sky",
        "fighting a shadow monster", "reading a holographic scroll",
        "drinking coffee in space", "playing chess with death",
        "dissolving into data", "blooming with flowers",
        "meditating on a mountain peak", "dancing in the void",
        "emerging from a portal", "reflected in a puddle",
        "inside a snow globe", "at the edge of the known universe",
        "during a solar eclipse", "in a field of bioluminescent flowers",
        "surrounded by floating lanterns", "inside a kaleidoscope",
        "walking on water", "in an infinite mirror room",
        "during cherry blossom rain", "at the bottom of the ocean",
        "inside a giant clockwork", "on a floating iceberg",
        "in a library of burning books", "at a crossroads between dimensions",
        "in a forest of mirrors", "during a meteor shower", "inside a drop of dew",
    ]

    # ── ПРОВЕРКА ПРАЗДНИКОВ ──
    def get_holiday_context():
        from datetime import datetime
        now = datetime.now()
        day_month = (now.day, now.month)
        
        holidays = {
            (1, 1): "New Year's Day. Magical winter atmosphere, festive lights, fireworks, cozy and epic celebrations.",
            (2, 1): "New Year holidays. Winter magic, snowy city, festive mood.",
            (7, 1): "Orthodox Christmas. Spiritual and cozy winter atmosphere, stars, snowy village, golden light.",
            (13, 1): "Old New Year. Retro winter aesthetic, nostalgic festive mood, snowy night.",
            (25, 1): "Tatiana Day (Students' Day). Young energy, books and coffee, winter university atmosphere.",
            (14, 2): "Valentine's Day. Romantic atmosphere, neon hearts, soft aesthetic, love and tenderness.",
            (23, 2): "Defender of the Fatherland Day (Feb 23). Epic military art, heroic protector, warrior soul, Russian landscape, courage, strength and honor.",
            (8, 3): "International Women's Day (March 8). Spring awakening, beautiful flowers, feminine elegance and power, soft bright colors.",
            (12, 4): "Cosmonautics Day. Yuri Gagarin, Soviet space aesthetic, first man in space, stars and rockets, retro-futurism.",
            (1, 5): "Spring and Labor Day. Sunny spring day, blossoming trees, joy, balloons and bright colors.",
            (9, 5): "Victory Day (May 9). Eternal flame, St. George ribbon, memory and honor, peaceful sky, spring flowers, military parade aesthetic.",
            (1, 6): "International Children's Day (June 1). Bright and joyful Russian childhood aesthetic, sunlit meadows, traditional toys, happiness and laughter, soft warm colors.",
            (12, 6): "Russia Day. Vast landscapes from Ural to Vladivostok, tricolor flag aesthetic, modern and traditional Russia.",
            (8, 7): "Family, Love and Fidelity Day. Chamomile flowers, warm family atmosphere, sunlit garden.",
            (22, 8): "National Flag Day. Russian tricolor in creative ways, patriotic aesthetic, blue sky.",
            (1, 9): "Knowledge Day. Golden autumn, school bells, books and backpacks, wise owl, library aesthetic.",
            (5, 10): "Teacher's Day. Books, autumn leaves, wisdom, cozy workspace, flowers for teacher.",
            (4, 11): "Unity Day. Historical heroic art, unity of people, Kremlin towers, traditional Russian spirit.",
            (31, 12): "New Year Eve. Olivier salad atmosphere, sparkling tree, magic, snowy night, lights and happiness."
        }
        return holidays.get(day_month)

    # ── ВЫБОР ТЕМЫ ──
    st1, st2, l, c = "Default", "Default", "Default", "Default"
    history = get_history()
    
    holiday_theme = get_holiday_context()

    if IS_SUNDAY_VIDEO:
        # ... (логика видео без изменений)
        s = random.choice(humor_subjects)
        for _ in range(20):
            if s in history: s = random.choice(humor_subjects)
            else: break
        save_to_history(s)
        t = f"Hyper-realistic and humorous video of {s}, positive vibe, vivid colors, morning inspiration"
        chosen_category = "Sunday Humor"
        t_prompt = f"Напиши ОЧЕНЬ СМЕШНОЙ и мотивационный пост на РУССКОМ языке про {s}. Используй много эмодзи! Текст должен быть ГРАМОТНЫМ и вдохновляющим. Структура JSON: TITLE, CONCEPT, TAGS."
    elif holiday_theme:
        print(f"🎉 СЕГОДНЯ ПРАЗДНИК! Тема: {holiday_theme}")
        t = holiday_theme
        chosen_category = "Holiday Special"
        st1, st2, l = "Epic cinematic", "Digital Illustration", "Dramatic Volumetric"
        s = "Holiday Celebration"
        t_prompt = f"Напиши торжественный, ГРАМОТНЫЙ и душевный поздравительный пост на РУССКОМ языке про {t}. Праздник сегодня! Используй красивые метафоры и много тематических эмодзи. Структура JSON: TITLE, CONCEPT, TAGS."
    else:
        # Категории с пониженным весом (уже надоели)
        low_weight_cats = {"Russian Spirit & Traditions", "Cyberpunk & Sci-Fi"}
        all_cats = list(categories.keys())
        # Строим взвешенный список: low_weight получают вес 1, остальные — 3
        weighted_cats = []
        for cat in all_cats:
            weighted_cats.extend([cat] * (1 if cat in low_weight_cats else 3))

        # 80% шанс — кросс-микс из 5 разных категорий
        use_crossmix = random.random() < 0.80
        if use_crossmix:
            used_cats, subjects = [], []
            for _ in range(5):
                available = [c for c in weighted_cats if c not in used_cats]
                if not available:
                    break
                cat = random.choice(available)
                used_cats.append(cat)
                subjects.append(random.choice(categories[cat]))
            connectors = ["meets", "collides with", "fused with", "reimagined as", "inside"]
            parts = [subjects[0]]
            for i, subj in enumerate(subjects[1:]):
                parts.append(f"{connectors[i % len(connectors)]} {subj}")
            s = " ".join(parts)
            chosen_category = " × ".join(used_cats)
        else:
            chosen_category = random.choice(weighted_cats)
            s = random.choice(categories[chosen_category])
            for _ in range(20):
                if s in history:
                    chosen_category = random.choice(weighted_cats)
                    s = random.choice(categories[chosen_category])
                else: break
        save_to_history(s)

        if chosen_category in ["Cyberpunk & Sci-Fi", "Space & Cosmos"]:
            possible_styles = style_groups["Futuristic/Cyber"] + style_groups["Modern/Digital"] + style_groups["Cinematic"]
            possible_lights = light_groups["Cyber/Neon"] + light_groups["Dramatic"]
        elif chosen_category in ["Fantasy & Myth", "Abstract & Surreal", "Horror & Dark"]:
            possible_styles = style_groups["Fantasy/Surreal"] + style_groups["Classic"] + style_groups["Cinematic"]
            possible_lights = light_groups["Dramatic"] + light_groups["Natural"] + ["Bioluminescence"]
        elif chosen_category in ["Nature & Bio-Mech", "Underwater World", "Micro World"]:
            possible_styles = style_groups["Modern/Digital"] + style_groups["Classic"] + style_groups["Cinematic"]
            possible_lights = light_groups["Natural"] + light_groups["Cyber/Neon"]
        else:
            possible_styles = style_groups["Classic"] + style_groups["Modern/Digital"] + style_groups["Cinematic"] + style_groups["Fantasy/Surreal"] + style_groups["Futuristic/Cyber"]
            possible_lights = light_groups["Natural"] + light_groups["Dramatic"] + light_groups["Cyber/Neon"]

        st1 = random.choice(possible_styles)
        st2 = random.choice(possible_styles)
        while st2 == st1: st2 = random.choice(possible_styles)
        l = random.choice(possible_lights)
        c = random.choice(contexts)
        qualifiers = "masterpiece, 8k, highly detailed, photorealistic, intricate textures, masterpiece composition, vivid colors, professionally rendered"
        t = f"{st1} and {st2} mix style of {s} {c}, with {l}, {qualifiers}"

    if CUSTOM_PROMPT:
        t = CUSTOM_PROMPT
        chosen_category = "Custom Request"
        st1, st2, l = "Custom", "Custom", "Custom"
        s = "Custom Subject"

    print(f"🎲 Категория: [{chosen_category}]")
    print(f"🎲 Стили: [{st1} + {st2}]")
    print(f"🎲 Свет: [{l}]")
    print(f"🎲 Тема: {t}")

    # ── ГЕНЕРАЦИЯ ТЕКСТА ──
    if PHOTO_MOOD_SUNDAY:
        t_prompt = f"Напиши ОЧЕНЬ СМЕШНОЙ, КИНЕМАТОГРАФИЧНЫЙ и мотивационный пост на РУССКОМ языке про {s}. Представь, что это кадр из эпической комедии! Используй много эмодзи. Структура JSON: TITLE, CONCEPT, TAGS. {RUSSIAN_GRAMMAR_PROMPT}"
    elif holiday_theme:
        t_prompt = f"Напиши торжественный, ГРАМОТНЫЙ и душевный поздравительный пост на РУССКОМ языке про {t}. Праздник сегодня! Передай истинную РУССКУЮ ЭСТЕТИКУ, используй красивые метафоры и тематические эмодзи. Структура JSON: TITLE, CONCEPT, TAGS. {RUSSIAN_GRAMMAR_PROMPT}"
    else:
        t_prompt = f"Write a creative Telegram post for the theme: {t}. Format: JSON with TITLE, CONCEPT, TAGS. {RUSSIAN_GRAMMAR_PROMPT}"

    print("📝 Генерирую текст под тему...")
    raw = generate_text_nvidia(t_prompt)
    if not raw:
        log_error("nvidia_text", "NVIDIA text generation returned None")
        print("⚠️ NVIDIA молчит. Пробую Kie.ai...")
        raw = generate_text_kie(t_prompt)
    if not raw:
        log_error("kie_text", "Kie text generation returned None")
        print("⚠️ Kie молчит. Пробую Groq...")
        raw = generate_text_groq(t_prompt)
    if not raw:
        log_error("groq_text", "Groq text generation returned None")
        print("⚠️ Groq молчит. Пробую OpenRouter...")
        raw = generate_text_openrouter(t_prompt)
    if not raw:
        print("⚠️ OpenRouter молчит. Пробую Gemini...")
        # The original Gemini prompt was different, modifying it to append RUSSIAN_GRAMMAR_PROMPT
        gemini_prompt = f"Post JSON about {t_prompt} in Russian. {{'TITLE':'...', 'CONCEPT':'...', 'TAGS':'...'}} {RUSSIAN_GRAMMAR_PROMPT}"
        raw = generate_text(gemini_prompt)
    if not raw:
        log_error("pollinations_text", "Pollinations text generation returned None")
        print("⚠️ Все молчат. Пробую Pollinations AI...")
        raw = generate_text_pollinations(t_prompt)
    
    if not raw:
        log_error("all_text_fallback", "ALL text generation providers failed.")
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: Ни одна нейросеть не смогла написать текст.")

    # Парсинг JSON
    title, concept, tags = None, None, None
    if raw:
        try:
            match = raw.replace('```json', '').replace('```', '').strip()
            start = match.find('{')
            end = match.rfind('}')
            if start != -1 and end != -1:
                data = json.loads(match[start:end+1])
                title = data.get('TITLE')
                concept = data.get('CONCEPT')
                tags = data.get('TAGS')
        except: pass

    if not title or not concept:
        print("🛠️ Аварийный шаблон...")
        title = f"🎨 {t[:40]}..."
        concept = "Погружение в мир цифровых грез и нейронных сетей."
        tags = "#AIArt #DigitalDreams #ArtBot"

    emojis = ["✨", "🔥", "🔮", "🎨", "🚀", "👁️", "🌊", "💎", "🌌", "🦾", "👾", "🐉", "🧬"]
    title = force_emoji(title, emojis)
    concept = force_emoji(concept, emojis)

    def clean_tags(tags_str):
        import re
        tokens = re.split(r'[\s,;|]+', str(tags_str or ''))
        result = []
        for t in tokens:
            t = t.strip().lstrip('#')
            t = re.sub(r'[\s\-&]+', '', t)
            if len(t) > 1:
                result.append(f'#{t}')
        return ' '.join(result[:6]) or '#AIArt'

    def esc(x): return str(x or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    tags_clean = clean_tags(tags)
    caption = f"✨ <b>{esc(title)}</b>\n\n{esc(concept)}\n\n{tags_clean}\n\n{YOUR_SIGNATURE}"
    if len(caption) > 1024: caption = caption[:1010] + "..."

    # Формируем target
    target = str(CHANNEL_ID).strip()
    if not (target.startswith('@') or target.startswith('-')):
        if target.isdigit():
            if not target.startswith('100') and not target.startswith('-'):
                target = f"-100{target}"
            elif target.startswith('100'):
                target = f"-{target}"
        else:
            target = f"@{target}"
    print(f"🎯 ЦЕЛЕВОЙ КАНАЛ: {target}")

    # ── ВИДЕО ──
    video_url = None
    if VIDEO_MODE:
        print(f"🎬 РЕЖИМ ВИДЕО! Генерирую через Kie.ai...")
        video_prompt = f"{t}, high realism, cinematic, smooth motion, 4k quality"
        video_url = generate_video_kie_and_poll(video_prompt, duration=5)
        if not video_url:
            print("❌ Видео не удалось сгенерировать. Завершаем — фото-пост не публикуем.")
            return

    # ── ИЗОБРАЖЕНИЕ (если не видео или видео не вышло) ──
    image_url, image_data = None, None
    provider_name = "Unknown"

    if not video_url:
        # ОСНОВНЫЕ МОДЕЛИ (Flux и другие)
        FLUX_MODELS = [
            {"name": "SiliconFlow (Flux Schnell)", "provider": "siliconflow", "model": "black-forest-labs/FLUX.1-schnell",       "key": SILICONFLOW_KEY},
            {"name": "HuggingFace (Flux Schnell)", "provider": "huggingface", "model": "black-forest-labs/FLUX.1-schnell",       "key": HF_KEY},
            {"name": "Cloudflare (Flux Schnell)",  "provider": "cloudflare",  "model": "@cf/black-forest-labs/flux-1-schnell",   "key": CLOUDFLARE_ID},
            {"name": "Airforce (Flux 1.1 Pro)",   "provider": "airforce",    "model": "flux-1.1-pro",    "key": True},
            {"name": "Pollinations (Flux Realism)","provider": "pollinations","model": "flux-realism",    "key": True},
            {"name": "Laozhang (DALL-E 3)",       "provider": "laozhang",    "model": "dall-e-3",                              "key": LAOZHANG_KEY},
            {"name": "Runware (100@1)",            "provider": "runware",     "model": "runware:100@1",                         "key": RUNWARE_KEY},
            {"name": "Gemini Image (Google)",      "provider": "gemini",      "model": "gemini-2.0-flash-exp", "key": GOOGLE_KEY},
        ]

        # ПРЕМИУМ МОДЕЛИ (Kie) — Только для праздников и Русской темы
        # Flux 2 Pro — лучшее качество для торжественных/русских тематик
        KIE_NANO_FRONT = [
            {"name": "Kie.ai (Flux 2 Pro)",      "provider": "kie_jobs",     "model": "flux-2/pro-text-to-image",   "key": KIE_KEY},
            {"name": "Kie.ai (Nano Banana Pro)", "provider": "kie_jobs",     "model": "nano-banana-pro",            "key": KIE_KEY},
            {"name": "Kie.ai (Nano Banana)",     "provider": "kie_jobs",     "model": "google/nano-banana",         "key": KIE_KEY},
        ]

        # ОБЫЧНЫЕ KIE МОДЕЛИ — Ideogram TURBO первый, затем Grok, Imagen4 Fast
        KIE_STANDARD_FRONT = [
            {"name": "Kie.ai (Ideogram v3 TURBO)", "provider": "kie_jobs", "model": "ideogram/v3-text-to-image", "key": KIE_KEY,
             "input_extra": {"rendering_speed": "TURBO", "style": "AUTO", "image_size": "square_hd", "num_images": "1"}},
            {"name": "Kie.ai (Grok Imagine)",    "provider": "kie_jobs",     "model": "grok-imagine/text-to-image", "key": KIE_KEY},
            {"name": "Kie.ai (Imagen 4 Fast)",   "provider": "kie_jobs",     "model": "google/imagen4-fast",        "key": KIE_KEY},
        ]

        # ЛОГИКА ОЧЕРЕДНОСТИ - Всегда KIE.ai первый, остальные как запасные
        is_rus_theme = chosen_category == "Russian Spirit & Traditions"
        if holiday_theme or is_rus_theme:
            print("🌟 ПРИОРИТЕТ: Праздник/Традиции. Используем Flux 2 Pro первым.")
            IMAGE_MODELS = KIE_NANO_FRONT + FLUX_MODELS
        else:
            print("🎨 ОБЫЧНЫЙ РЕЖИМ: Ideogram TURBO -> Grok -> Imagen4 Fast.")
            IMAGE_MODELS = KIE_STANDARD_FRONT + FLUX_MODELS

        print(f"🎨 Начинаем генерацию. Доступно провайдеров: {len(IMAGE_MODELS)}")

        for model_cfg in IMAGE_MODELS:
            if not model_cfg['key']: continue
            p_name = model_cfg['name']
            p_type = model_cfg['provider']
            if "Picsum" not in p_name: print(f"👉 Пробуем: {p_name}...")

            try:
                # ── KIE.AI ПРОВАЙДЕРЫ (обновлено февраль 2026) ──
                if p_type in ("kie_jobs", "kie_4o", "kie_flux"):
                    print(f"🎨 Kie.ai создание задачи ({model_cfg['model']})...")
                    kie_headers = {"Authorization": f"Bearer {model_cfg['key']}", "Content-Type": "application/json"}
                    task_id = None
                    try:
                        # Разные эндпоинты для разных типов моделей
                        if p_type == "kie_4o":
                            url = "https://api.kie.ai/api/v1/gpt4o-image/generate"
                            payload = {"prompt": t}
                        elif p_type == "kie_flux":
                            url = "https://api.kie.ai/api/v1/flux/kontext/generate"
                            payload = {"model": model_cfg['model'], "prompt": t}
                        else:  # kie_jobs
                            url = "https://api.kie.ai/api/v1/jobs/createTask"
                            job_input = {"prompt": t, "aspect_ratio": "1:1"}
                            job_input.update(model_cfg.get('input_extra', {}))
                            payload = {"model": model_cfg['model'], "input": job_input}

                        r = requests.post(url, json=payload, headers=kie_headers, timeout=60)
                        if r.status_code == 200:
                            res = r.json()
                            if res.get('code') in [200, None]:
                                d = res.get('data', {})
                                if isinstance(d, dict):
                                    task_id = d.get('taskId') or d.get('recordId') or d.get('id')
                                elif isinstance(d, str):
                                    task_id = d
                                if not task_id:
                                    task_id = res.get('taskId') or res.get('id')
                            else:
                                print(f"⚠️ Kie.ai API Error {res.get('code')}: {res.get('msg', '')[:150]}")
                        else:
                            print(f"⚠️ Kie.ai HTTP {r.status_code}: {r.text[:200]}")

                        if task_id:
                            print(f"⏳ Картинка в очереди (ID: {task_id}). Ожидаем...")
                            poll_url = "https://api.kie.ai/api/v1/jobs/recordInfo"
                            for attempt in range(20):
                                time.sleep(8)
                                pr = requests.get(f"{poll_url}?taskId={task_id}", headers=kie_headers, timeout=30)
                                if pr and pr.status_code == 200:
                                    p_res = pr.json()
                                    s_data = p_res.get('data', {})
                                    if not isinstance(s_data, dict): s_data = {}
                                    state = s_data.get('state', '')
                                    if s_data.get('failCode') and str(s_data.get('failCode')) not in ['0', 'None', '']:
                                        print(f"❌ Kie.ai Failed (failCode={s_data.get('failCode')})")
                                        break
                                    res_json_str = s_data.get('resultJson', '')
                                    if res_json_str:
                                        try:
                                            res_obj = json.loads(res_json_str)
                                            urls = res_obj.get('resultUrls', [])
                                            if urls:
                                                image_url = urls[0]
                                                print(f"✅ Kie.ai Image OK: {image_url}")
                                                break
                                        except: pass
                                    if state in ('fail', 'failed', 'error'):
                                        print(f"❌ Kie.ai задача провалилась: state={state}")
                                        break
                            if image_url: break
                    except Exception as ex:
                        print(f"⚠️ Kie.ai Image Exception: {ex}")

                elif p_type == "laozhang":
                    r = requests.post("https://api.laozhang.ai/v1/images/generations",
                                      json={"model": model_cfg['model'], "prompt": t, "n": 1, "size": "1024x1024"},
                                      headers={"Authorization": f"Bearer {model_cfg['key']}", "Content-Type": "application/json"}, timeout=60)
                    if r.status_code == 200: image_url = r.json()['data'][0]['url']
                    else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

                elif p_type == "siliconflow":
                    r = requests.post("https://api.siliconflow.cn/v1/images/generations",
                                      json={"model": model_cfg['model'], "prompt": t, "image_size": "1024x1024", "batch_size": 1},
                                      headers={"Authorization": f"Bearer {SILICONFLOW_KEY}", "Content-Type": "application/json"}, timeout=45)
                    if r.status_code == 200: image_url = r.json()['images'][0]['url']
                    else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

                elif p_type == "runware":
                    r = requests.post("https://api.runware.ai/v1",
                                      json=[{"action": "authentication", "api_key": RUNWARE_KEY},
                                            {"action": "image_inference", "modelId": model_cfg['model'], "positivePrompt": t, "width": 1024, "height": 1024}],
                                      timeout=45)
                    if r.status_code == 200:
                        d = r.json().get('data', [])
                        if d and d[0].get('imageURL'): image_url = d[0]['imageURL']
                    else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

                elif p_type == "huggingface":
                    hf_headers = {"Authorization": f"Bearer {HF_KEY}"}
                    r = requests.post(f"https://router.huggingface.co/hf-inference/models/{model_cfg['model']}", headers=hf_headers, json={"inputs": t}, timeout=60)
                    if r.status_code == 200: image_data = io.BytesIO(r.content)
                    else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

                elif p_type == "cloudflare":
                    cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ID}/ai/run/{model_cfg['model']}"
                    r = requests.post(cf_url, headers={"Authorization": f"Bearer {CLOUDFLARE_TOKEN}"}, json={"prompt": t}, timeout=60)
                    if r.status_code == 200: image_data = io.BytesIO(r.content)
                    else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

                elif p_type == "airforce":
                    r = requests.post("https://api.airforce/v1/images/generations",
                                      json={"model": model_cfg['model'], "prompt": t, "size": "1024x1024"}, timeout=55)
                    if r.status_code == 200: image_url = r.json()['data'][0]['url']
                    elif r.status_code == 429: print("   ⚠️ Rate Limit (429)")
                    else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

                elif p_type == "pollinations":
                    encoded = urllib.parse.quote(t)
                    seed = random.randint(1, 99999)
                    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model={model_cfg['model']}&nologo=true&seed={seed}"
                    r = requests.get(url, timeout=60)
                    if r.status_code == 200 and len(r.content) > 5000: image_data = io.BytesIO(r.content)
                    else: log_error(p_type, f"HTTP {r.status_code} or small content: {r.text[:200]}")

                elif p_type == "gemini":
                    image_data = generate_image_gemini(t)

                elif p_type == "horde":
                    horde_url = "https://stablehorde.net/api/v2/generate/async"
                    h_headers = {"apikey": "0000000000", "Client-Agent": "FriendLeeBot:4.0"}
                    payload = {"prompt": t, "params": {"width": 512, "height": 512}, "models": ["ICBINP - I Can't Believe It's Not Photography"]}
                    r = requests.post(horde_url, json=payload, headers=h_headers, timeout=30)
                    if r.status_code == 202:
                        req_id = r.json()['id']
                        for _ in range(8):
                            time.sleep(5)
                            stat = requests.get(f"https://stablehorde.net/api/v2/generate/status/{req_id}", headers=h_headers).json()
                            if stat['done']:
                                image_url = stat['generations'][0]['img']
                                break
                        if not image_url:
                            log_error(p_type, "Timeout or no result after polling.")
                    else: log_error(p_type, f"HTTP {r.status_code}: {r.text[:200]}")

                elif p_type == "picsum":
                    r = requests.get(f"https://picsum.photos/seed/{random.randint(1,1000)}/1024/1024")
                    if r.status_code == 200: image_data = io.BytesIO(r.content)
                    else: log_error(p_type, f"HTTP {r.status_code}: {r.text[:200]}")

                if image_url or image_data:
                    provider_name = p_name
                    print(f"✅ УСПЕХ! Генерация выполнена через: {p_name}")
                    break
                else:
                    log_error(p_type, f"{p_name} failed to return image data/url")

            except Exception as e:
                log_error(p_type, str(e))
                continue

    # ── ОТПРАВКА ──
    if not video_url and not image_url and not image_data:
        raise Exception("CRITICAL: Ни видео ни картинка не сгенерированы.")

    if image_data:
        try:
            image_data.seek(0)
            img = Image.open(image_data)
            img.verify()
            image_data.seek(0)
            print(f"✅ Image Verified: {img.format}")
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            image_data = None
            if not image_url and not video_url:
                raise Exception("Incomplete Art Data.")

    for attempt in range(3):
        try:
            print(f"📤 Attempt {attempt+1}: Sending to {target}...")
            if video_url:
                bot.send_video(target, video_url, caption=caption, parse_mode='HTML', supports_streaming=True)
            elif image_url:
                bot.send_photo(target, image_url, caption=caption, parse_mode='HTML')
            else:
                image_data.seek(0)
                bot.send_photo(target, image_data, caption=caption, parse_mode='HTML')
            print("🎉 SUCCESS! Content posted.")
            return
        except Exception as e:
            print(f"❌ Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(15)
            else:
                raise

# ─────────────────────────────────────────────
# ПЛАНИРОВЩИК И ЗАЩИТА (WATCHDOG)
# ─────────────────────────────────────────────

execution_lock = threading.Lock()
last_post_time = datetime.min

def safe_run_final():
    """Обертка для запуска с логированием и защитой от зависаний"""
    global last_post_time
    # Пытаемся захватить лок, чтобы не запускать два поста одновременно
    if not execution_lock.acquire(blocking=False):
        print("⚠️ [Watchdog] Пропуск: Другая генерация уже запущена.")
        return

    try:
        print(f"🚀 [Watchdog] Запуск генерации: {datetime.now().strftime('%H:%M:%S')}")
        run_final()
        last_post_time = datetime.now()
        print("✅ [Watchdog] Пост успешно опубликован.")
    except Exception as e:
        print(f"❌ [Watchdog] Критическая ошибка генерации: {e}")
        # Если ошибка произошла, watchdog увидит, что время последнего поста старое, и попробует снова через цикл
    finally:
        execution_lock.release()

def scheduler_thread():
    """Улучшенный планировщик с контролем выхода постов"""
    print("⏰ Внутренний планировщик и Watchdog запущены...")
    
    # Расписание (МСК время)
    post_times = ["09:07", "14:07", "19:07", "21:07", "22:07"]
    
    for t in post_times:
        schedule.every().day.at(t).do(safe_run_final)

    while True:
        try:
            schedule.run_pending()
            
            # WATCHDOG ЛОГИКА (Задержка максимум 10 минут)
            now = datetime.now()
            for t_str in post_times:
                t_hour, t_min = map(int, t_str.split(':'))
                sched_today = now.replace(hour=t_hour, minute=t_min, second=0, microsecond=0)
                
                # Если прошло больше 10 минут с момента плана, а поста не было
                if timedelta(minutes=10) < (now - sched_today) < timedelta(hours=2):
                    if last_post_time < sched_today:
                        print(f"⚠️ [Watchdog] ОБНАРУЖЕНА ЗАДЕРЖКА поста {t_str}! Форсирую запуск...")
                        # Запускаем в отдельном потоке, чтобы не вешать цикл
                        threading.Thread(target=safe_run_final, daemon=True).start()
            
        except Exception as e:
            print(f"⚠️ Ошибка в цикле планировщика: {e}")
            
        time.sleep(30) # Проверка каждые 30 секунд

# ─────────────────────────────────────────────
# ОБРАБОТЧИКИ КОМАНД (для сервера)
# ─────────────────────────────────────────────

if bot:
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "🚀 <b>Бот работает на сервере!</b>\n\nМогу делать посты по расписанию и выполнять команды.\n/generate — форсировать создание арта", parse_mode='HTML')

    @bot.message_handler(commands=['generate'])
    def force_generate(message):
        bot.send_message(message.chat.id, "🎨 Начинаю внеплановую генерацию...")
        try:
            safe_run_final()
            bot.send_message(message.chat.id, "✅ Генерация завершена!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

if __name__ == "__main__":
    if "--server" in sys.argv:
        print("🖥️ ЗАПУСК В РЕЖИМЕ СЕРВЕРА (Polling + Watchdog)")
        t = threading.Thread(target=scheduler_thread, daemon=True)
        t.start()
        
        if bot:
            print("🤖 Listening for commands...")
            bot.infinity_polling()
        else:
            print("❌ BOT_TOKEN не найден. Режим сервера невозможен.")
            while True: time.sleep(1)
    elif "--test" in sys.argv:
        print("🧪 ЗАПУСК ПРИНУДИТЕЛЬНОГО ТЕСТА...")
        # Принудительно ставим категорию
        sys.argv.append("--custom-prompt")
        sys.argv.append("Russian Fairytale Village, hyper-realistic, russian spirit aesthetic, 8k")
        run_final()
    else:
        run_final()
