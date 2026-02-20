print("🚀 BOOTING FRIE-ND-LEE ART BOT...")
# God Mode V3.0 Activated (Trigger: 2026-02-19 22:35)
import telebot
import os
import requests
import random
import urllib.parse
import base64
import json
import time # Added for sleep
import io
from PIL import Image

# НОВЫЙ КЛЮЧ
# --- КОНФИГУРАЦИЯ (Берем из секретов GitHub) ---
GOOGLE_KEY = os.environ.get('GOOGLE_KEY')
SILICONFLOW_KEY = os.environ.get('SILICONFLOW_KEY')
RUNWARE_KEY = os.environ.get('RUNWARE_KEY')
HF_KEY = os.environ.get('HF_KEY')
KIE_KEY = os.environ.get('KIE_KEY')
CLOUDFLARE_ID = os.environ.get('CLOUDFLARE_ID')
CLOUDFLARE_TOKEN = os.environ.get('CLOUDFLARE_TOKEN')

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')
YOUR_SIGNATURE = os.environ.get('YOUR_SIGNATURE', "@fRieNDLee34")

bot = telebot.TeleBot(TOKEN) if TOKEN else None

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

def generate_text(theme):
    if not GOOGLE_KEY:
        return None
    print("📝 Gemini пишет текст...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_KEY}"
    
    if "JSON" in theme:
        final_prompt = theme
    else:
        final_prompt = f"Write a JSON post about {theme}."

    payload = {
        "contents": [{
            "parts": [{"text": final_prompt}]
        }]
    }
    
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return None

def generate_text_pollinations(theme):
    print("🧠 Pollinations AI (Backup Brain) пишет текст...")
    prompt = (
        f"Ты креативный SMM-менеджер арт-канала. Напиши пост про '{theme}'. "
        f"ЯЗЫК: Русский (Заголовок, Концепт, Описание) и Английский (Prompt). "
        f"СТРУКТУРА ОТВЕТА (строго JSON): "
        f'{{"TITLE": "...", "CONCEPT": "...", "DESCRIPTION": "...", "PROMPT": "..."}} '
        f"TITLE: Цепляющий заголовок с эмодзи. "
        f"CONCEPT: Смешная или глубокая предыстория (3-4 предложения). "
        f"DESCRIPTION: Атмосферное описание визуала. "
        f"PROMPT: Detailed, high-quality English prompt for image generation (8k, cinematic, intricate details). "
        f"Сделай это живо, весело и креативно!"
    )
    try:
        # Pollinations Text API (GET request usually works well for simple prompts)
        # We use a trick to get JSON-like cleaning
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai&seed={random.randint(1, 9999)}"
        r = requests.get(url, timeout=60)
        return r.text
    except Exception as e:
        print(f"Pollinations Text Error: {e}")
        return None

def generate_text_kie(theme):
    print("🧠 Kie.ai (DeepSeek) пишет текст...")
    url = "https://api.kie.ai/v1/chat/completions" # Проверим эндпоинт, обычно совместим с OpenAI
    headers = {
        "Authorization": f"Bearer {KIE_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"Ты восхищенный зритель в галерее будущего. Напиши пост про арт '{theme}'.\n"
        f"Требования:\n"
        f"1. Язык: РУССКИЙ (без ошибок!).\n"
        f"2. Стиль: Вдохновленный поэт цифровой эпохи. ЭМОЦИОНАЛЬНО! 💖\n"
        f"3. ОБЪЕМ: Концепт - 20-30 слов.\n"
        f"4. ЭМОДЗИ: СТРОГО НАЧИНАЙ И ЗАКАНЧИВАЙ КАЖДУЮ ФРАЗУ СМАЙЛОМ (🔥, ✨, 😱, 🌌)!\n"
        f"5. ФОРМАТ JSON: {{\"TITLE\": \"...\", \"CONCEPT\": \"...\", \"TAGS\": \"...\"}}\n"
        f"TITLE: Заголовок КАПСОМ.\n"
        f"CONCEPT: Описание философии арта (только одна секция!).\n"
        f"TAGS: 5-7 тегов на английском (#Art #Futurism ...)."
    )
    
    payload = {
        "model": "deepseek-v3", # Пробуем v3 или chatgpt-4o-latest (зависит от доступа)
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
             print(f"Kie.ai Error: {r.text}")
             return None
    except Exception as e:
        print(f"Kie.ai Exception: {e}")
        return None

import feedparser

def get_ai_news():
    print("📰 Ищу свежие новости про ИИ...")
    feeds = [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
    ]
    try:
        for url in feeds:
            feed = feedparser.parse(url)
            if feed.entries:
                entry = random.choice(feed.entries[:5]) # Берем одну из 5 свежих
                return f"News: {entry.title}"
    except Exception as e:
        print(f"RSS Error: {e}")
    return None

# --- ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ ЧЕРЕЗ GEMINI ---
def generate_image_gemini(prompt):
    """Генерирует картинку через Gemini 2.5 Flash Image (бесплатно с GOOGLE_KEY)"""
    if not GOOGLE_KEY:
        return None
    print("🎨 Gemini Image генерирует картинку...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={GOOGLE_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Generate a beautiful, high-quality digital art image: {prompt}"}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]}
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
            print(f"⚠️ Gemini Image: нет картинки в ответе. Response: {r.text[:300]}")
        else:
            print(f"⚠️ Gemini Image Error: {r.text[:300]}")
    except Exception as e:
        print(f"⚠️ Gemini Image Exception: {e}")
    return None

import sys
import uuid

def run_final():
    print(f"--- FrieNDLee_FTP BOT (v2.0) 🚀 ---")

    # --- EMOJI ENFORCER ---
    def force_emoji(text, pool):
        if not text: return ""
        # Проверяем, есть ли смайлы
        has_emoji = any(char in text for char in pool)
        if not has_emoji:
             return f"{random.choice(pool)} {text} {random.choice(pool)}"
        return text
    
    # ПРОВЕРКА НА ТЕСТОВЫЙ РЕЖИМ
    TEST_MODE = "--test" in sys.argv
    FORCE_SOURCE = None

    # 1. ШАГ: РЕШАЕМ ОТКУДА БРАТЬ ИДЕЮ
    # Только Reddit или Внутренний генератор (Новостей нет)
    # ... (rest of code)


    # --- 1. ШАГ: РЕШАЕМ ОТКУДА БРАТЬ ИДЕЮ ---
    source = "INTERNAL"
    t = None
    
    # 50% шанс Reddit
    if random.random() < 0.5:
        print("🌍 Ищу вдохновение на Reddit...")
        subreddits = ["Art", "DigitalArt", "Cyberpunk", "ImaginaryLandscapes", "Midjourney", "StableDiffusion-Concepts"]
        bsub = random.choice(subreddits)
        try:
            r_url = f"https://www.reddit.com/r/{bsub}/top.json?limit=15&t=day"
            resp = requests.get(r_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if resp.status_code == 200:
                posts = resp.json()['data']['children']
                valid_posts = [p['data']['title'] for p in posts if not p['data']['stickied']]
                if valid_posts:
                    theme_core = random.choice(valid_posts)
                    t = f"Art inspired by: {theme_core}"
                    source = f"REDDIT (r/{bsub})"
                    print(f"🔥 НАЙДЕН ТРЕНД: {theme_core}")
        except Exception as e:
            print(f"⚠️ Ошибка Reddit: {e}")

    # Если Reddit не сработал -> 30% Новости ИИ
    if not t and random.random() < 0.3:
        news_theme = get_ai_news()
        if news_theme:
            t = f"Artistic interpretation of: {news_theme}"
            source = "AI NEWS"
            print(f"📰 ТЕМА ИЗ НОВОСТЕЙ: {news_theme}")

    # Если всё еще нет темы -> ВНУТРЕННИЙ ГЕНЕРАТОР (GOD MODE V3.0)
    if not t:
        subjects = [
            # Cyberpunk & Sci-Fi (Hardcore)
            "Old Cyberpunk Wizard", "Futuristic Samurai", "Neon Noir Detective", "Cyborg Geisha", 
            "High-Tech Astronaut", "Post-Apocalyptic Stalker", "Quantum Computer Core", "Mech Warrior",
            "Holographic AI Entity", "Time Traveler in Void", "Space Marine with Plasma Sword", 
            "Android with Porcelain Skin", "Glitch in Matrix", "Dyson Sphere", "Flying Car Chase",
            "Cyber-Monk Meditating", "Nanotech Swarm", "Robot playing Violin", "Hacker in VR",
            "Retro-Futuristic TV Head Character", "Cassette Futurism Dashboard", "Atompunk City",
            "Soviet Cyberpunk Panel Building", "Cybernetic Pharaoh", "Neon Demon", "Ghost in the Shell",
            
            # Fantasy & Myth (Epic)
            "Ethereal Goddess", "Viking Warlord", "Mythical Dragon", "Ancient Greek Statue with Neon",
            "Crystal Golem", "Phoenix Rising from Ashes", "Elf Archer with Laser Bow", "Necromancer in City",
            "Floating Island Castle", "Magic Potion Shop", "Forest Spirit", "Demon Hunter", "Vampire Lord",
            "Werewolf in Suit", "Ghost Ship inside Bottle", "Mermaid in Toxic Ocean", "Fallen Angel",
            "Cthulhu in Cyberpunk City", "Skeleton playing Saxophone", "Knight fighting Dragon in Space",
            "Anubis with Laser Eyes", "Medusa with Fiber Optic Hair", "Valkyrie on Hoverbike",
            
            # Nature & Bio-Mech (Weird)
            "Biomechanical Tiger", "Cosmic Jellyfish", "Steampunk Owl", "Clockwork Heart", 
            "Electric Eel in Sky", "Crystal Flower", "Liquid Metal Cat", "Tree of Life in Space",
            "Mushroom Kingdom", "Lava Turtle", "Frozen Lightning", "Nebula in a Jar", "DNA Helix Galaxy",
            "Snail with Tiny House", "Whale floating over City", "Spider made of Glass", "Radioactive Butterfly",
            "Fox with 9 Tails of Fire", "Owl made of Books", "Lion made of Stars",
            
            # Abstract & Surreal (Mind-Bending)
            "Fractal Soul", "Melting Clocks in Desert", "Stairway to Heaven", "Mirror Dimension",
            "Human Silhouette made of Stars", "Exploding Color Dust", "Liquid Gold River", 
            "Glass Chess Board", "Portal to Another World", "Brain connected to Universe",
            "Eye of the Storm", "Sound Waves visible", "Time Frozen in Amber", "Universe inside a Marble",
            "Tiny World inside a Lightbulb", "Shipwreck in a Desert", "Oasis in Cyber-Wasteland",
            "Chess Game between God and Devil", "Doorway in the Middle of Ocean",
            
            # Architecture & Places (Grand)
            "Futuristic Skyscraper", "Abandoned Space Station", "Underwater Hotel", "Cloud City", 
            "Cyberpunk Street Food Cart", "Temple of Lost Technology", "Library of Infinite Books", 
            "Neon Jungle", "Mars Colony Greenhouse", "Vertical Forest City", "Gothic Cathedral in Space",
            "Brutalist Concrete Bunker", "Art Deco Spaceport", "Pyramid of Glass", "Infinite Hallway",
            
            # Fashion & Avant-Garde
            "Model in Liquid Glass Dress", "Cyber-Fashion Runway", "Mask made of Diamonds",
            "Dress made of Smoke", "Suit made of Mirrors", "Shoes made of Lava", "Cyber-Goth Rave"
        ]
        
        styles = [
            "Unreal Engine 5 Render", "Octane Render", "Redshift Render", "V-Ray", "Blender Cycles",
            "Hyper-realistic Photo", "8k Raw Photo", "Macro Lens Detail", "Long Exposure", 
            "Cinematic Shot", "Cyber-Renaissance", "Biopunk", "Solvedpunk", 
            "Vaporwave", "Synthwave", "Gothic Futurism", "Baroque Sci-Fi", 
            "Rococo Cyberpunk", "Pop Art Neon", "Glitch Art", "Bauhaus Style", "Voxel Art"
        ]
        
        lighting = [
            "Volumetric Lighting", "Bioluminescence", "Neon Glow", "God Rays", "Rim Lighting", 
            "Cinematic Color Grading", "Dark Contrast", "Pastel Soft Light", "Cyber-Blue Bloom", 
            "Golden Hour", "Midnight Rain Reflections", "Cyber-Green Haze", "Rembrandt Lighting"
        ]
        
        contexts = [
            "in heavy rain at night", "standing on a cliff edge", 
            "surrounded by floating crystals", "in a neon-lit alleyway", 
            "with glowing eyes", "under a double moon sky",
            "fighting a shadow monster", "reading a holographic scroll",
            "drinking coffee in space", "playing chess with death",
            "dissolving into data", "blooming with flowers",
            "meditating on a mountain peak", "dancing in the void"
        ]
        
        s = random.choice(subjects)
        st1 = random.choice(styles)
        st2 = random.choice(styles)
        l = random.choice(lighting)
        c = random.choice(contexts)
        t = f"{st1} and {st2} style of {s} {c}, with {l}, masterpiece, 8k, detailed"
        print(f"🎲 Сгенерирована тема (God Mode V3.0): {t}")
    
        # --- 2. ШАГ: ГЕНЕРИРУЕМ ТЕКСТ (ЗАГОЛОВОК, КОНЦЕПТ, ТЕГИ) ---
    headers_common = {"User-Agent": "Mozilla/5.0"}
    
    # 1. Текст от Gemini
    print("📝 Gemini пишет текст...")
    raw = generate_text(f"Post JSON about {t} in Russian. {{'TITLE':'...', 'CONCEPT':'...', 'TAGS':'...'}}")
    
    # 2. Если Gemini молчит -> Kie.ai
    if not raw:
        print("⚠️ Gemini молчит. Пробую Kie.ai...")
        raw = generate_text_kie(t)
        
    # 3. Если и Kie молчит -> Pollinations
    if not raw:
        print("⚠️ Все молчат. Пробую Pollinations AI...")
        raw = generate_text_pollinations(t)

    # ПАРСИНГ И FALLBACK
    title, concept, tags = None, None, None
    if raw:
        import json
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

    def esc(s): return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    caption = f"✨ <b>{esc(title)}</b>\n\n{esc(concept)}\n\n{esc(tags) or '#AIArt'}\n\n{YOUR_SIGNATURE}"
    if len(caption) > 1024: caption = caption[:1010] + "..."

    target = str(CHANNEL_ID)
    if not target.startswith('@') and not target.startswith('-'):
        if not target.isdigit(): target = f"@{target}"

    # --- 3. ШАГ: РИСУЕМ (ROBUST LOOP V2) ---
    image_url, image_data = None, None
    provider_name = "Unknown"

    # СПИСОК МОДЕЛЕЙ (В порядке приоритета: Ключи -> Бесплатные Про -> Бесплатные Обычные -> Резерв)
    IMAGE_MODELS = [
        # --- TIER 1: PAID / KEYS (High Stability) ---
        {"name": "SiliconFlow (Flux Schnell)", "provider": "siliconflow", "model": "black-forest-labs/FLUX.1-schnell", "key": SILICONFLOW_KEY},
        {"name": "Runware (100@1)", "provider": "runware", "model": "runware:100@1", "key": RUNWARE_KEY},
        {"name": "HuggingFace (Flux Schnell)", "provider": "huggingface", "model": "black-forest-labs/FLUX.1-schnell", "key": HF_KEY},
        {"name": "Cloudflare (Flux Schnell)", "provider": "cloudflare", "model": "@cf/black-forest-labs/flux-1-schnell", "key": CLOUDFLARE_ID},
        
        # --- TIER 2: FREE API (Airforce - Often Good) ---
        {"name": "Airforce (Flux 1.1 Pro)", "provider": "airforce", "model": "flux-1.1-pro", "key": True},
        {"name": "Airforce (Flux 1 Dev)", "provider": "airforce", "model": "flux-1-dev", "key": True},
        {"name": "Airforce (Flux Schnell)", "provider": "airforce", "model": "flux-1-schnell", "key": True},
        {"name": "Airforce (Any Dark)", "provider": "airforce", "model": "any-dark", "key": True},
        
        # --- TIER 3: POLLINATIONS (Always Free, Good Quality) ---
        {"name": "Pollinations (Flux Realism)", "provider": "pollinations", "model": "flux-realism", "key": True},
        {"name": "Pollinations (Midjourney)", "provider": "pollinations", "model": "midjourney", "key": True},
        {"name": "Pollinations (Flux)", "provider": "pollinations", "model": "flux", "key": True},
        {"name": "Pollinations (Turbo)", "provider": "pollinations", "model": "turbo", "key": True},
        
        # --- TIER 4: FALLBACKS ---
        {"name": "Gemini Image (Google)", "provider": "gemini", "model": "gemini-2.5-flash-image", "key": GOOGLE_KEY},
        {"name": "AI Horde (SDXL Beta)", "provider": "horde", "model": "SDXL_beta_examples", "key": True},
        {"name": "Picsum (Stock Photo)", "provider": "picsum", "model": "photo", "key": True},
    ]

    print(f"🎨 Начинаем генерацию. Доступно провайдеров: {len(IMAGE_MODELS)}")

    for model_cfg in IMAGE_MODELS:
        if not model_cfg['key']: continue # Пропуск если нет ключа
            
        p_name = model_cfg['name']
        p_type = model_cfg['provider']
        
        # Simple logging to allow user to see progress
        if "Picsum" not in p_name: print(f"👉 Пробуем: {p_name}...")
        
        try:
            # --- PROVIDER LOGIC ---
            if p_type == "siliconflow":
                r = requests.post("https://api.siliconflow.cn/v1/images/generations", 
                                 json={"model": model_cfg['model'], "prompt": t, "image_size": "1024x1024", "batch_size": 1},
                                 headers={"Authorization": f"Bearer {SILICONFLOW_KEY}", "Content-Type": "application/json"}, timeout=45)
                if r.status_code == 200: 
                    image_url = r.json()['images'][0]['url']
            
            elif p_type == "runware":
                r = requests.post("https://api.runware.ai/v1", 
                                 json=[{"action": "authentication", "api_key": RUNWARE_KEY},
                                       {"action": "image_inference", "modelId": model_cfg['model'], "positivePrompt": t, "width": 1024, "height": 1024}], 
                                 timeout=45)
                if r.status_code == 200:
                    d = r.json().get('data', [])
                    if d and d[0].get('imageURL'): image_url = d[0]['imageURL']

            elif p_type == "huggingface":
                 headers = {"Authorization": f"Bearer {HF_KEY}"}
                 r = requests.post(f"https://router.huggingface.co/{model_cfg['model']}", headers=headers, json={"inputs": t}, timeout=60)
                 if r.status_code == 200: image_data = io.BytesIO(r.content)

            elif p_type == "cloudflare":
                cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ID}/ai/run/{model_cfg['model']}"
                r = requests.post(cf_url, headers={"Authorization": f"Bearer {CLOUDFLARE_TOKEN}"}, json={"prompt": t}, timeout=60)
                if r.status_code == 200: image_data = io.BytesIO(r.content)

            elif p_type == "airforce":
                # Using standard OpenAI-like endpoint for Airforce
                url = "https://api.airforce/v1/images/generations"
                r = requests.post(url, json={"model": model_cfg['model'], "prompt": t, "size": "1024x1024"}, timeout=55)
                if r.status_code == 200: image_url = r.json()['data'][0]['url']
                elif r.status_code == 429: print("   ⚠️ Rate Limit (429)")

            elif p_type == "pollinations":
                encoded = urllib.parse.quote(t)
                seed = random.randint(1, 99999)
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model={model_cfg['model']}&nologo=true&seed={seed}"
                r = requests.get(url, timeout=60)
                if r.status_code == 200 and len(r.content) > 5000: image_data = io.BytesIO(r.content)

            elif p_type == "gemini":
                image_data = generate_image_gemini(t)

            elif p_type == "horde":
                 # Fallback to simple Horde sync-like check (or fire-and-forget logic if needed, but here blocking is safer for script)
                 # Re-implementing simplified Horde logic
                 horde_url = "https://stablehorde.net/api/v2/generate/async"
                 h_headers = {"apikey": "0000000000", "Client-Agent": "FriendLeeBot:2.0"}
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

            elif p_type == "picsum":
                r = requests.get(f"https://picsum.photos/seed/{random.randint(1,1000)}/1024/1024")
                if r.status_code == 200: image_data = io.BytesIO(r.content)

            # --- SUCCESS CHECK ---
            if image_url or image_data:
                provider_name = p_name
                print(f"✅ УСПЕХ! Генерация выполнена через: {p_name}")
                break
            
        except Exception as e:
            # print(f"⚠️ {p_name} Error: {e}") # Uncomment for deeper debug
            continue

    # --- 4. ШАГ: ОТПРАВКА ---
    if not image_url and not image_data: raise Exception("CRITICAL: All Art Engines failed.")
    
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
            if not image_url: raise Exception("Incomplete Art Data.")

    try:
        if image_url: 
            bot.send_photo(target, image_url, caption=caption, parse_mode='HTML')
        else:
            image_data.seek(0)
            bot.send_photo(target, image_data, caption=caption, parse_mode='HTML')
        print("🎉 SUCCESS! Art posted.")
    except Exception as e:
        print(f"❌ SENDING FAILED: {e}")
        raise

if __name__ == "__main__":
    run_final()
