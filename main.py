# Trigger Comment for GitHub Actions
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


    # 1. ШАГ: РЕШАЕМ ОТКУДА БРАТЬ ИДЕЮ
    source = "INTERNAL"
    reddit_theme = None
    
    # Логика выбора источника (с учетом флага)
    use_reddit = (random.random() < 0.5)
    if FORCE_SOURCE == "REDDIT": use_reddit = True
    elif FORCE_SOURCE == "INTERNAL": use_reddit = False
    
    if use_reddit:
        print("🌍 Ищу вдохновение на Reddit...")
        subreddits = ["Art", "DigitalArt", "Cyberpunk", "ImaginaryLandscapes", "Midjourney", "StableDiffusion", "ConceptArt"]
        bsub = random.choice(subreddits)
        try:
            r_url = f"https://www.reddit.com/r/{bsub}/top.json?limit=15&t=day"
            resp = requests.get(r_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if resp.status_code == 200:
                posts = resp.json()['data']['children']
                valid_posts = [p['data']['title'] for p in posts if not p['data']['stickied']]
                if valid_posts:
                    reddit_theme = random.choice(valid_posts)
                    t = f"Art inspired by: {reddit_theme}"
                    source = f"REDDIT (r/{bsub})"
                    print(f"🔥 НАЙДЕН ТРЕНД: {reddit_theme}")
        except Exception as e:
            print(f"⚠️ Ошибка Reddit: {e}. Перехожу на внутренний генератор.")

    if not reddit_theme:
        # 30% шанс взять реальную новость про ИИ, если нет Reddit
        if random.random() < 0.3:
            news_theme = get_ai_news()
            if news_theme:
                t = f"Artistic interpretation of: {news_theme}"
                print(f"📰 ТЕМА ИЗ НОВОСТЕЙ: {news_theme}")
            else:
                 # Фолбек на генератор
                 pass 
        
        # ВНУТРЕННИЙ ГЕНЕРАТОР (MEGA-EXPANSION V2.0)
        subjects = [
            # Cyberpunk & Sci-Fi
            "Old Cyberpunk Wizard", "Futuristic Samurai", "Neon Noir Detective", "Cyborg Geisha", 
            "High-Tech Astronaut", "Post-Apocalyptic Stalker", "Quantum Computer Core", "Mech Warrior",
            "Holographic AI Entity", "Time Traveler in Void", "Space Marine with Plasma Sword", 
            "Android with Porcelain Skin", "Glitch in Matrix", "Dyson Sphere", "Flying Car Chase",
            "Cyber-Monk Meditating", "Nanotech Swarm", "Robot playing Violin", "Hacker in VR",
            
            # Fantasy & Myth
            "Ethereal Goddess", "Viking Warlord", "Mythical Dragon", "Ancient Greek Statue with Neon",
            "Crystal Golem", "Phoenix Rising from Ashes", "Elf Archer with Laser Bow", "Necromancer in City",
            "Floating Island Castle", "Magic Potion Shop", "Forest Spirit", "Demon Hunter", "Vampire Lord",
            "Werewolf in Suit", "Ghost Ship inside Bottle", "Mermaid in Toxic Ocean", "Fallen Angel",
            
            # Nature & Bio-Mech
            "Biomechanical Tiger", "Cosmic Jellyfish", "Steampunk Owl", "Clockwork Heart", 
            "Electric Eel in Sky", "Crystal Flower", "Liquid Metal Cat", "Tree of Life in Space",
            "Mushroom Kingdom", "Lava Turtle", "Frozen Lightning", "Nebula in a Jar", "DNA Helix Galaxy",
            
            # Abstract & Surreal
            "Fractal Soul", "Melting Clocks in Desert", "Stairway to Heaven", "Mirror Dimension",
            "Human Silhouette made of Stars", "Exploding Color Dust", "Liquid Gold River", 
            "Glass Chess Board", "Portal to Another World", "Brain connected to Universe",
            "Eye of the Storm", "Sound Waves visible", "Time Frozen in Amber",
            
            # Architecture & Places
            "Futuristic Skyscraper", "Abandoned Space Station", "Underwater Hotel", "Cloud City", 
            "Cyberpunk Street Food Cart", "Temple of Lost Technology", "Library of Infinite Books", 
            "Neon Jungle", "Mars Colony Greenhouse", "Vertical Forest City", "Gothic Cathedral in Space"
        ]
        
        styles = [
            # Rendering
            "Unreal Engine 5 Render", "Octane Render", "Redshift Render", "V-Ray", "Blender Cycles",
            "Cinema 4D", "Unity Engine", "Lumen Global Illumination", "Ray Tracing",
            
            # Photography
            "Hyper-realistic Photo", "8k Raw Photo", "Macro Lens Detail", "Long Exposure", 
            "Bokeh Depth of Field", "Fish-eye Lens", "Drone Shot", "Studio Lighting", 
            "National Geographic Style", "Polaroid Vintage", "Double Exposure", "Tilt-Shift",
            
            # Artistic
            "Cinematic Shot", "Dark Moody Texture", "Cyber-Renaissance", "Biopunk", "Solvedpunk", 
            "Dieselpunk", "Vaporwave", "Synthwave", "Gothic Futurism", "Baroque Sci-Fi", 
            "Rococo Cyberpunk", "Abstract Expressionism", "Surrealism", "Pop Art Neon",
            "Ukiyo-e Cyber Style", "Oil Painting Impasto", "Watercolor Splatter", "Ink Wash Painting",
            "Marble Sculpture", "Glass Blowing Art", "Origami Paper Art", "Low Poly 3D"
        ]
        
        lighting = [
            "Volumetric Lighting", "Bioluminescence", "Neon Glow", "God Rays", "Rim Lighting", 
            "Cinematic Color Grading", "Dark Contrast", "Pastel Soft Light", "Cyber-Blue Bloom", 
            "Golden Hour", "Midnight Rain Reflections"
        ]
        
        contexts = [
            "in heavy rain at night", "standing on a cliff edge", 
            "surrounded by floating crystals", "in a neon-lit alleyway", 
            "with glowing eyes", "reflecting in a puddle", 
            "in a dense misty forest", "under a double moon sky",
            "fighting a shadow monster", "reading a holographic scroll",
            "drinking coffee in space", "playing chess with death",
            "dissolving into data", "blooming with flowers",
            "frozen in time", "burning with cold fire"
        ]
        
        s = random.choice(subjects)
        st1 = random.choice(styles)
        st2 = random.choice(styles) # Smeshivaem stili
        l = random.choice(lighting)
        c = random.choice(contexts)
        
        # Super-Combo Prompt
        t = f"{st1} and {st2} of a {s} {c}, {l}, highly detailed, sharp focus, masterpiece, 8k, trending on artstation"
        print(f"🎲 Сгенерирована тема (Mix): {t}")
    
    
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
    # ----------------------------------------------------
    image_url = None
    image_data = None # Для Cloudflare (base64 bytes)
    
    # Попытка №1: SiliconFlow
    print("🎨 SiliconFlow (FLUX.1) начинает работу...")
    try:
        sf_url = "https://api.siliconflow.cn/v1/images/generations"
        sf_headers = {"Authorization": f"Bearer {SILICONFLOW_KEY}", "Content-Type": "application/json"}
        sf_payload = {"model": "black-forest-labs/FLUX.1-schnell", "prompt": prompt, "image_size": "1024x1024", "num_inference_steps": 4}
        sf_resp = requests.post(sf_url, json=sf_payload, headers=sf_headers, timeout=60)
        if sf_resp.status_code == 200:
            image_url = sf_resp.json()['data'][0]['url']
            print(f"✅ УСПЕХ: Картинка (SiliconFlow): {image_url[:50]}...")
        else:
            print(f"⚠️ Ошибка SiliconFlow: {sf_resp.text}")
    except Exception as e:
        print(f"⚠️ Сбой SiliconFlow: {e}")

    # Попытка №2: Runware
    if not image_url and not image_data:
        print("⚡ Runware (Backup) начинает работу...")
        try:
            rw_url = "https://api.runware.ai/v1"
            rw_headers = {"Content-Type": "application/json"}
            rw_payload = [{"taskType": "authentication", "apiKey": RUNWARE_KEY}, 
                          {"taskType": "imageInference", "taskUUID": str(uuid.uuid4()), 
                           "positivePrompt": prompt, "width": 1024, "height": 1024, "modelId": "runware:100@1"}]
            rw_resp = requests.post(rw_url, json=rw_payload, headers=rw_headers, timeout=30)
            if rw_resp.status_code == 200:
                for item in rw_resp.json().get('data', []):
                    if item.get('taskType') == "imageInference" and item.get('imageURL'):
                        image_url = item['imageURL']
                        print(f"✅ УСПЕХ: Картинка (Runware): {image_url[:50]}...")
                        break
            else:
                 print(f"⚠️ Ошибка Runware: {rw_resp.text}")
        except Exception as e:
            print(f"⚠️ Сбой Runware: {e}")

    # Попытка №2.5: Hugging Face (NEW!)
    if not image_url and not image_data:
        print("🤗 Hugging Face (Backup) начинает работу...")
        try:
            hf_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            hf_headers = {"Authorization": f"Bearer {HF_KEY}"}
            hf_payload = {"inputs": prompt}
            hf_resp = requests.post(hf_url, json=hf_payload, headers=hf_headers, timeout=50)
            if hf_resp.status_code == 200:
                # HF возвращает бинарник (image/jpeg)
                image_data = hf_resp.content
                print(f"✅ УСПЕХ: Картинка (Hugging Face) сгенерирована!")
            else:
                 print(f"⚠️ Ошибка Hugging Face: {hf_resp.text}")
        except Exception as e:
            print(f"⚠️ Сбой Hugging Face: {e}")

    # Попытка №3: Cloudflare
    if not image_url and not image_data:
        print("☁️ Cloudflare (Backup #2) начинает работу...")
        try:
            cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
            cf_headers = {"Authorization": f"Bearer {CLOUDFLARE_TOKEN}"}
            cf_payload = {"prompt": prompt, "num_steps": 4}
            cf_resp = requests.post(cf_url, json=cf_payload, headers=cf_headers, timeout=50)
            if cf_resp.status_code == 200:
                import base64
                image_data = base64.b64decode(cf_resp.json()['result']['image'])
                print(f"✅ УСПЕХ: Картинка (Cloudflare) сгенерирована!")
            else:
                 print(f"⚠️ Ошибка Cloudflare: {cf_resp.text}")
        except Exception as e:
            print(f"⚠️ Сбой Cloudflare: {e}")

    # ----------------------------------------------------
    # 3. ШАГ: ПОСТИНГ
    # ----------------------------------------------------
    caption = (
        f"{title}\n\n"
        f"{concept}\n\n"
        f"{tags}\n"
        f"{YOUR_SIGNATURE}"
    )

    if len(caption) > 1024:
        caption = caption[:1000] + f"\n{YOUR_SIGNATURE}"

    if TEST_MODE:
        print(f"📝 Caption:\n{caption}")
        return

    # Если есть URL (от SiliconFlow или Runware) -> Отправляем как ФОТО
    if image_url:
        try:
            bot.send_photo(CHANNEL_ID, image_url, caption=caption, parse_mode='HTML')
            print("🎉 ПОБЕДА! Фото отправлено!")
            return
        except Exception as e:
            print(f"❌ Не удалось отправить фото (Url Error): {e}")

    # Если есть данные (Cloudflare) -> Отправляем как ФОТО
    if image_data:
        try:
            bot.send_photo(CHANNEL_ID, image_data, caption=caption, parse_mode='HTML')
            print("🎉 ПОБЕДА! Фото (Bytes) отправлено!")
            return
        except Exception as e:
            print(f"❌ Не удалось отправить фото (Bytes Error): {e}")
    
    # ПЛАН C: Pollinations (Image Download Mode)
    print("🔄 ПЛАН C: Pollinations (Download Mode)...")
    poll_url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt[:500])}?width=1024&height=1024&model=flux&nologo=true"
    try:
        # Скачиваем картинку в память (с заголовками браузера!)
        fake_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        img_resp = requests.get(poll_url, headers=fake_headers, timeout=60)
        if img_resp.status_code == 200:
            bot.send_photo(CHANNEL_ID, io.BytesIO(img_resp.content), caption=caption, parse_mode='HTML')
            print("🎉 ПОБЕДА! Фото (Pollinations) отправлено!")
            return
    except Exception as e:
        print(f"⚠️ Ошибка Pollinations Download: {e}")
        
    # Если даже скачать не вышло - ПЛАН D (Сдача)
    # Мы больше не шлем ссылки текстом, чтобы не мусорить в канале.
    print("❌ Все методы загрузки фото провалились. Пост отменен.")

if __name__ == "__main__":
    run_final()
