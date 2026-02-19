print("🚀 BOOTING FRIE-ND-LEE ART BOT...")
# God Mode V3.0 Activated (Trigger: 2026-02-19 21:05)
import telebot
import os
import requests
import random
import io
import urllib.parse
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_KEY}"
    
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
    
    
    # 1. Текст от Kie.ai (PRIORITY - DeepSeek лучше пишет по-русски)
    raw = generate_text_kie(t)
    
    # 2. Если Kie сломался -> Gemini
    if not raw:
        print("⚠️ Kie.ai молчит. Пробую Gemini...")
        gemini_prompt = (
            f"Напиши ОЧЕНЬ КОРОТКИЙ пост про '{t}'.\n"
            f"Язык: Русский. Эмоций: МНОГО (используй ✨🔥).\n"
            f"Концепт: мах 15 слов.\n"
            f"JSON: {{\"TITLE\": \"...\", \"CONCEPT\": \"...\", \"TAGS\": \"...\"}}"
        )
        raw = generate_text(gemini_prompt)

    # 3. Если и Gemini сломался -> Pollinations
    if not raw:
        print("⚠️ Gemini молчит. Пробую Pollinations AI...")
        raw = generate_text_pollinations(t)

    # 3. ЕСЛИ ВСЕ СЛОМАЛОСЬ -> РАСШИРЕННЫЙ АВТОНОМНЫЙ РЕЖИМ
    if not raw:
        print("⚠️ Все AI-писатели недоступны. Включаю 'Генератор Шаблонов v3.0'...")
        title_emoji = random.choice(["✨", "🔥", "🔮", "🎨", "🚀", "👁️", "🌊", "💎", "🌌"])
        title = f"{title_emoji} {t.upper()} {title_emoji}"
        
        # Генератор более сложных промптов на английском
        adjectives = ["cinematic lighting", "hyper-realistic", "ethereal", "dreamlike", "volumetric lighting", "octane render", "intricate details", "4k", "8k", "studio quality", "sharp focus", "bokeh", "vivid colors", "dynamic composition"]
        art_styles = ["cyberpunk style", "oil painting", "watercolor style", "digital art", "concept art", "fantasy art", "sci-fi", "anime style", "photorealism"]
        selected_adjectives = ", ".join(random.sample(adjectives, 5))
        selected_style = random.choice(art_styles)
        prompt = f"masterpiece, best quality, {t}, {selected_style}, {selected_adjectives}, highly detailed, trending on artstation"
        
        # ... (concepts_bank logic remains)
        concepts_bank = [
             f"Искусство — это {t}. Всё остальное — просто шум.",
             "Творческий хаос, который обрел форму.",
             "Эстетический восторг в каждом пикселе.",
             "Нейросеть снова превзошла саму себя.",
             "Идеальный баланс света и тени."
        ]
        descriptions_bank = ["<i>Каждая деталь здесь рассказывает свою историю.</i>", "<i>Свет падает так реалистично, что хочется протянуть руку.</i>"]
        
        concept = random.choice(concepts_bank)
        description = random.choice(descriptions_bank)

    else:
        # Парсинг (Gemini или Pollinations)
        import json
        val = {}
        # Очистка markdown (```json ... ```)
        clean_raw = raw.replace('```json', '').replace('```', '').strip()
        
        # Попытка найти первую { и последнюю } для извлечения JSON
        start_idx = clean_raw.find('{')
        end_idx = clean_raw.rfind('}')
        if start_idx != -1 and end_idx != -1:
            clean_raw = clean_raw[start_idx:end_idx+1]
        
        try:
            val = json.loads(clean_raw)
        except:
             # Fallback parsing
             pass
        
        title = val.get('TITLE', f"✨ {t.upper()} ✨")
        concept = val.get('CONCEPT', 'Уникальный взгляд на цифровое искусство.')
        tags = val.get('TAGS', '#AIArt #DigitalArt #Masterpiece')
        # Промпт генерируем для внутреннего пользования, но не показываем
        prompt = f"masterpiece, best quality, {t}, 8k, detailed"
        
        # --- EMOJI ENFORCER ---
        emojis = ["✨", "🔥", "🔮", "🎨", "🚀", "👁️", "🌊", "💎", "🌌", "🦾", "👾", "🐉", "🧬"]
        title = force_emoji(title, emojis)
        concept = force_emoji(concept, emojis)
        # ----------------------
        
    # ----------------------------------------------------
    # 2. ШАГ: РИСУЕМ (1. SiliconFlow -> 2. Runware -> 3. Cloudflare -> 4. Pollinations)
    # ----------------------------------------------    # --- 3. ШАГ: ГЕНЕРИРУЕМ КАРТИНКУ ---
    image_url = None
    image_data = None
    
    # ПЛАН A: SiliconFlow (Primary)
    if SILICONFLOW_KEY:
        print(f"🎨 SiliconFlow (FLUX.1) начинает работу... (Баланс может быть 0)")
        sf_url = "https://api.siliconflow.cn/v1/images/generations"
        headers = {"Authorization": f"Bearer {SILICONFLOW_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": t,
            "negative_prompt": "nsfw, low quality, blurry, distorted, watermarks",
            "image_size": "1024x1024",
            "batch_size": 1
        }
        try:
            r = requests.post(sf_url, json=payload, headers=headers, timeout=45)
            if r.status_code == 200:
                image_url = r.json()['images'][0]['url']
                print("✅ SiliconFlow: URL получен.")
            else:
                 print(f"⚠️ Ошибка SiliconFlow: {r.text}")
        except Exception as e:
            print(f"⚠️ Исключение SiliconFlow: {e}")

    # ПЛАН B: Runware (Secondary)
    if not image_url and RUNWARE_KEY:
        print("⚡ Runware (Backup) начинает работу...")
        rw_url = "https://api.runware.ai/v1"
        rw_payload = [
            {"action": "authentication", "api_key": RUNWARE_KEY},
            {
                "action": "image_inference",
                "modelId": "runware:100@1", # Flux.1 Schnell
                "positivePrompt": t,
                "width": 1024, "height": 1024, "numberResults": 1, "outputType": "URL"
            }
        ]
        try:
            r = requests.post(rw_url, json=rw_payload, timeout=45)
            if r.status_code == 200:
                res = r.json().get('data', [])
                for item in res:
                    if 'imageURL' in item:
                        image_url = item['imageURL']
                        print("✅ Runware: URL получен.")
                        break
            else:
                 print(f"⚠️ Ошибка Runware: {r.text}")
        except Exception as e:
            print(f"⚠️ Исключение Runware: {e}")

    # ПЛАН B.1: Hugging Face (Backup #2)
    if not image_url and HF_KEY:
        print("🤗 Hugging Face (Backup) начинает работу...")
        hf_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_KEY}"}
        try:
            r = requests.post(hf_url, headers=headers, json={"inputs": t}, timeout=60)
            if r.status_code == 200:
                image_data = io.BytesIO(r.content)
                print("✅ Hugging Face: Данные получены.")
            else:
                 print(f"⚠️ Ошибка Hugging Face: {r.text}")
        except Exception as e:
            print(f"⚠️ Исключение Hugging Face: {e}")

    # ПЛАН B.2: Cloudflare (Backup #3)
    if not image_url and not image_data and CLOUDFLARE_TOKEN and CLOUDFLARE_ID:
        print("☁️ Cloudflare (Backup #3) начинает работу...")
        cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
        headers = {"Authorization": f"Bearer {CLOUDFLARE_TOKEN}"}
        try:
            r = requests.post(cf_url, headers=headers, json={"prompt": t}, timeout=60)
            if r.status_code == 200:
                image_data = io.BytesIO(r.content)
                print("✅ Cloudflare: Данные получены.")
            else:
                 print(f"⚠️ Ошибка Cloudflare: {r.text}")
        except Exception as e:
            print(f"⚠️ Исключение Cloudflare: {e}")

    # --- 4. ШАГ: ОТПРАВКА В ТЕЛЕГРАМ ---
    if not image_url and not image_data:
        # ПЛАН C: Pollinations (Download Mode) - ПОСЛЕДНЯЯ НАДЕЖДА
        print("🔄 ПЛАН C: Pollinations (Download Mode)...")
        poll_url = f"https://pollinations.ai/p/{urllib.parse.quote(t[:500])}?width=1024&height=1024&model=flux&nologo=true"
        try:
            fake_headers = {"User-Agent": "Mozilla/5.0"}
            img_resp = requests.get(poll_url, headers=fake_headers, timeout=60)
            if img_resp.status_code == 200:
                image_data = io.BytesIO(img_resp.content)
                print("✅ Pollinations: Фото скачано.")
            else:
                print(f"❌ Pollinations недоступен: {img_resp.status_code}")
        except Exception as e:
            print(f"⚠️ Ошибка Pollinations: {e}")

    if not image_url and not image_data:
        print(f"❌ ВСЕ МЕТОДЫ ПРОВАЛИЛИСЬ. Тема: {t}")
        raise Exception("God Mode: No images generated.")

    # Отправка
    try:
        if image_url:
            bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='HTML')
        else:
            bot.send_photo(CHANNEL_ID, image_data, caption=caption, parse_mode='HTML')
        print("🎉 ПОБЕДА! Пост в канале.")
    except Exception as e:
        print(f"❌ ОШИБКА ОТПРАВКИ: {e}")
        raise

if __name__ == "__main__":
    run_final()
