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
GROQ_KEY = os.environ.get('GROQ_KEY')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')
LAOZHANG_KEY = os.environ.get('LAOZHANG_KEY')

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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_KEY}"
    
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

def generate_text_groq(theme):
    if not GROQ_KEY: return None
    print("🧠 Groq API пишет текст (Llama 3)...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    prompt = (
        f"Ты креативный SMM-менеджер арт-канала. Напиши пост про '{theme}'. "
        f"ЯЗЫК: Русский (Заголовок, Концепт, Описание) и Английский (Prompt). "
        f"СТРУКТУРА ОТВЕТА (строго JSON): "
        f'{{"TITLE": "...", "CONCEPT": "...", "DESCRIPTION": "...", "TAGS": "..."}} '
        f"TITLE: Цепляющий заголовок с эмодзи. "
        f"CONCEPT: Смешная или глубокая предыстория. "
        f"TAGS: 3-5 тегов через #."
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
    if not KIE_KEY: return None
    print("🧠 Kie.ai (DeepSeek) пишет текст...")
    # Используем актуальный эндпоинт для чата
    url = "https://api.kie.ai/v1/chat/completions" 
    headers = {
        "Authorization": f"Bearer {KIE_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"Напиши JSON пост про арт '{theme}'. ЯЗЫК: РУССКИЙ. "
        f"СТРУКТУРА: {{\"TITLE\": \"...\", \"CONCEPT\": \"...\", \"TAGS\": \"...\"}}. "
        f"Будь эмоциональным и используй много эмодзи!"
    )
    
    payload = {
        "model": "deepseek-v3", # Или "chatgpt-4o-latest", "gpt-4o"
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        if r.status_code == 200:
            res_json = r.json()
            # Добавим проверку структуры ответа
            if 'choices' in res_json and len(res_json['choices']) > 0:
                return res_json['choices'][0]['message']['content']
            else:
                print(f"⚠️ Kie.ai Unexpected JSON: {res_json}")
                return None
        else:
            print(f"⚠️ Kie.ai Error {r.status_code}: {r.text}")
            return None
    except Exception as e:
        print(f"⚠️ Kie.ai Exception: {e}")
        return None

# --- УДАЛЕНО: Reddit и Новости ИИ больше не используются ---

# --- ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ ЧЕРЕЗ GEMINI ---
def generate_video_kie(prompt, model="sora-2-text-to-video", duration=10, size="landscape"):
    """Генерирует видео через Kie.ai (Актуальные эндпоинты)"""
    if not KIE_KEY:
        print("❌ Ошибка: KIE_KEY не задан.", flush=True)
        return None
    
    # Регуляция модели
    if model == "sora-2":
        model = "sora-2-text-to-video"
    
    print(f"🎬 Kie.ai Video ({model}) создание задачи...", flush=True)
    # Исправленный эндпоинт согласно документации
    url = "https://api.kie.ai/api/v1/jobs/createTask"
    headers = {
        "Authorization": f"Bearer {KIE_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "n_frames": str(duration),
            "aspect_ratio": size,
            "remove_watermark": True
        }
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"📡 API Create Status: {r.status_code}", flush=True)
        try:
            res_data = r.json()
            print(f"📦 API Message: {res_data.get('message', 'No message')}", flush=True)
        except:
            print(f"📦 API Raw: {r.text[:500]}", flush=True)
            return None

        if r.status_code == 200:
            # В новом API task_id может быть в 'data' или в корне
            task_id = res_data.get('taskId') or res_data.get('id')
            if not task_id and 'data' in res_data:
                if isinstance(res_data['data'], dict):
                    task_id = res_data['data'].get('taskId') or res_data['data'].get('id')
                elif isinstance(res_data['data'], str):
                    task_id = res_data['data']

            if not task_id:
                print(f"⚠️ Task ID not found. Data: {res_data}", flush=True)
                return None
            
            print(f"⏳ Видео в очереди (ID: {task_id}). Ожидание...", flush=True)
            
            # Поллинг - taskId как query параметр
            poll_base_url = "https://api.kie.ai/api/v1/jobs/recordInfo"
            max_attempts = 50 
            for attempt in range(max_attempts):
                time.sleep(20)
                try:
                    pr = requests.get(f"{poll_base_url}?taskId={task_id}", headers=headers, timeout=30)
                    if pr.status_code == 200:
                        status_data = pr.json()
                        data_part = status_data.get('data', {})
                        if not isinstance(data_part, dict): data_part = {}
                        
                        # Kie.ai recordInfo возвращает resultJson (строка JSON внутри JSON)
                        result_json_str = data_part.get('resultJson', '')
                        fail_code = data_part.get('failCode', '')
                        
                        # Логируем каждые 10 попыток
                        if attempt % 10 == 0:
                            print(f"   [{attempt+1}] resultJson len={len(result_json_str)}, failCode={fail_code}", flush=True)
                        else:
                            print(f"   [{attempt+1}] ожидание... (resultJson={bool(result_json_str)})", flush=True)
                        
                        # Если есть failCode — провал
                        if fail_code and str(fail_code) not in ['', '0', 'None']:
                            print(f"❌ Провал (failCode={fail_code}): {data_part}", flush=True)
                            return None
                        
                        # Если resultJson не пустой — парсим
                        if result_json_str:
                            try:
                                result_obj = json.loads(result_json_str)
                                result_urls = result_obj.get('resultUrls', [])
                                print(f"   [{attempt+1}] Найдено URL: {len(result_urls)}", flush=True)
                                
                                if result_urls and len(result_urls) > 0:
                                    v_url = result_urls[0]
                                    print(f"✅ ВИДЕО ГОТОВО: {v_url}", flush=True)
                                    return v_url
                            except json.JSONDecodeError as je:
                                print(f"   [{attempt+1}] Не удалось распарсить resultJson: {je}", flush=True)
                    else:
                        print(f"⚠️ Ошибка опроса ({pr.status_code})", flush=True)
                except Exception as e:
                    print(f"⚠️ Ошибка сети: {e}", flush=True)
            
            print("🛑 Превышено время ожидания.", flush=True)

        else:
            print(f"⚠️ Ошибка API ({r.status_code}): {r.text[:500]}", flush=True)
    except Exception as e:
        print(f"⚠️ Ошибка запроса: {e}", flush=True)
    return None

def generate_image_gemini(prompt):
    """Генерирует картинку через Gemini 2.5 Flash Image (бесплатно с GOOGLE_KEY)"""
    if not GOOGLE_KEY:
        return None
    print("🎨 Gemini Image генерирует картинку...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"Generate a beautiful, high-quality digital art image: {prompt}"}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
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
    VIDEO_MODE = "--video" in sys.argv
    FORCE_SOURCE = None


    # ПРОВЕРКА НА АВТО-ВИДЕО (Воскресенье 22:00 МСК = 19:00 UTC)
    from datetime import datetime, timezone, timedelta
    now_utc = datetime.now(timezone.utc)
    msk_delta = timedelta(hours=3)
    now_msk = now_utc + msk_delta
    
    print(f"🕒 Текущее время (МСК): {now_msk.strftime('%Y-%m-%d %H:%M:%S')}")
    
    IS_SUNDAY_VIDEO = False
    # Если воскресенье (6) и время 22:00 (час 22-23 для надежности) ИЛИ запущен ручной режим видео
    if (now_msk.weekday() == 6 and now_msk.hour in [22, 23]) or "--video" in sys.argv:
        if now_msk.weekday() == 6 and now_msk.hour in [22, 23]:
            print("🕒 АВТО-РЕЖИМ: Воскресенье (Видео-пост).")
        else:
            print("🧪 ТЕСТ-РЕЖИМ: Ручная активация юмористического видео.")
        
        VIDEO_MODE = True
        IS_SUNDAY_VIDEO = True

    # === МЕГА-БИБЛИОТЕКА КОНЦЕПЦИЙ (РАСШИРЕНА В 2 РАЗА) ===
    # Добавляем спец-категорию для юмора
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
        "A group of robots having a messy pillow fight in a high-tech lab"
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
            "Floating Temple above Clouds", "Crystal Cave City",
            "San Francisco year 2100", "Floating Venice of the Future", "Mayan Temple with Holograms",
            "Steampunk London with Zeppelins", "Treehouse Village in Giant Forest",
            "Moon Village Observatory", "Desert Mirage Oasis", "Glass Bridge over Lava",
            "Ice Palace in Antarctica", "Cybernetic Colosseum", "Vertical Slums of Neo-Tokyo",
            "Rainbow Waterfall City", "Zero-G Concert Hall", "Ancient Cave with Bioluminescence",
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
    }
    
    styles = [
        "Unreal Engine 5 Render", "Octane Render", "Redshift Render", "V-Ray", "Blender Cycles",
        "Hyper-realistic Photo", "8k Raw Photo", "Macro Lens Detail", "Long Exposure", "Tilt-Shift Photo",
        "DSLR Portrait", "Film Noir Photography", "Infrared Photography", "Double Exposure Photo",
        "Cinematic Shot", "Anamorphic Lens Flare", "IMAX Wide Angle", "Drone Aerial View",
        "Cyber-Renaissance", "Biopunk", "Solarpunk", "Steampunk Digital", "Dieselpunk Art",
        "Vaporwave", "Synthwave", "Gothic Futurism", "Baroque Sci-Fi", 
        "Rococo Cyberpunk", "Pop Art Neon", "Glitch Art", "Bauhaus Style", "Voxel Art",
        "Art Nouveau Digital", "Ukiyo-e Modern", "Afrofuturism", "Stained Glass Art",
        "Low Poly Art", "Pixel Art HD", "Watercolor Digital", "Oil Painting Realistic",
        "Chalk Art Photorealistic", "Comic Book Style", "Anime Cinematic", "Studio Ghibli Inspired",
        "Dark Fantasy Illustration", "Concept Art for AAA Game", "Ethereal Oil Painting",
        "Cubism Modern", "Impressionism Digital", "Surrealism Dali Style", "Pencil Sketch Detailed",
    ]
    
    lighting = [
        "Volumetric Lighting", "Bioluminescence", "Neon Glow", "God Rays", "Rim Lighting", 
        "Cinematic Color Grading", "Dark Contrast", "Pastel Soft Light", "Cyber-Blue Bloom", 
        "Golden Hour", "Midnight Rain Reflections", "Cyber-Green Haze", "Rembrandt Lighting",
        "Northern Lights Aurora", "Candlelight Warm Glow", "Laser Grid Light",
        "Sunset Silhouette", "Moonlight Silver Glow", "Neon Pink and Blue Split",
        "Underwater Caustics", "Firefly Bokeh", "Studio Dramatic Spotlight",
        "Holographic Rainbow Refraction", "Eclipse Shadow Light", "Lightning Strike Flash",
        "Fluorescent Tube Light", "Street Light Shadows", "Optical Fiber Glow",
    ]
    
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
    
    # ВЫБОР ТЕМЫ
    if IS_SUNDAY_VIDEO:
        s = random.choice(humor_subjects)
        t = f"Hyper-realistic and humorous video of {s}, positive vibe, vivid colors, morning inspiration"
        chosen_category = "Sunday Humor"
    else:
        chosen_category = random.choice(list(categories.keys()))
        s = random.choice(categories[chosen_category])
        st1 = random.choice(styles)
        st2 = random.choice(styles)
        while st2 == st1: st2 = random.choice(styles)
        l = random.choice(lighting)
        c = random.choice(contexts)
        qualifiers = "masterpiece, 8k, highly detailed, photorealistic, intricate textures, masterpiece composition, vivid colors, professionally rendered"
        t = f"{st1} and {st2} mix style of {s} {c}, with {l}, {qualifiers}"
    
    print(f"🎲 Категория: [{chosen_category}]")
    print(f"🎲 Сгенерирована тема (God Mode V4.0): {t}")

    # ЕСЛИ ВОСКРЕСЕНЬЕ - МЕНЯЕМ ПРОМПТ ДЛЯ ТЕКСТА
    if IS_SUNDAY_VIDEO:
        t_prompt = f"Write a VERY FUNNY and MOTIVATIONAL Russian post about {s}. Use many emojis! The goal is to make people happy for Monday morning. Structure: TITLE, CONCEPT, TAGS."
    else:
        t_prompt = t

    # --- 2. ШАГ: ГЕНЕРИРУЕМ ТЕКСТ ---
    print("📝 Генерирую текст под тему...")
    # 1. Сначала Kie.ai (приоритет - купленный ключ)
    raw = generate_text_kie(t_prompt)
    
    # 2. Если Kie молчит -> Groq
    if not raw:
        print("⚠️ Kie молчит. Пробую Groq...")
        raw = generate_text_groq(t_prompt)

    # 3. Если Groq молчит -> OpenRouter
    if not raw:
        print("⚠️ Groq молчит. Пробую OpenRouter...")
        raw = generate_text_openrouter(t_prompt)

    # 4. Если OpenRouter молчит -> Gemini
    if not raw:
        print("⚠️ OpenRouter молчит. Пробую Gemini...")
        raw = generate_text(f"Post JSON about {t_prompt} in Russian. {{'TITLE':'...', 'CONCEPT':'...', 'TAGS':'...'}}")
        
    # 5. Если и Gemini молчит -> Pollinations
    if not raw:
        print("⚠️ Все молчат. Пробую Pollinations AI...")
        raw = generate_text_pollinations(t_prompt)

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

    target = str(CHANNEL_ID).strip()
    if not (target.startswith('@') or target.startswith('-')):
        if target.isdigit():
            # Если это просто число, Telegram требует чтобы ID начинался с -100 для каналов
            if not target.startswith('100') and not target.startswith('-'):
                target = f"-100{target}"
            elif target.startswith('100'):
                target = f"-{target}"
        else:
            target = f"@{target}"

    video_url = None
    if VIDEO_MODE:
        print(f"🎬 РЕЖИМ ВИДЕО АКТИВИРОВАН! Модель: Sora 2")
        # Для видео добавим приписку о реализме, как просил пользователь
        video_prompt = f"{t}, high realism, cinematic style, detailed, 4k"
        video_url = generate_video_kie(video_prompt, model="sora-2-text-to-video", duration=10, size="landscape")
        if not video_url:
            print("⚠️ Видео не удалось сгенерировать. Пробуем фото как запасной вариант.")
            VIDEO_MODE = False # Отключаем режим видео для этого прогона
    
    image_url, image_data = None, None
    provider_name = "Unknown"

    # СПИСОК МОДЕЛЕЙ (В порядке приоритета: Ключи -> Бесплатные Про -> Бесплатные Обычные -> Резерв)
    IMAGE_MODELS = [
        # --- TIER 1: KIE.AI (MAIN PRIORITY) ---
        {"name": "Kie.ai (Flux Kontext)", "provider": "kie_image", "model": "flux-1-kontext", "key": KIE_KEY},
        {"name": "Kie.ai (Flux Pro)", "provider": "kie_image", "model": "flux-1-pro", "key": KIE_KEY},
        {"name": "Kie.ai (SDXL)", "provider": "kie_image", "model": "stable-diffusion-xl", "key": KIE_KEY},

        # --- TIER 2: OTHER PAID KEYS (Backup) ---
        {"name": "Laozhang (DALL-E 3)", "provider": "laozhang", "model": "dall-e-3", "key": LAOZHANG_KEY},
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
        {"name": "Gemini Image (Google)", "provider": "gemini", "model": "gemini-2.0-flash-exp", "key": GOOGLE_KEY},
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
            if p_type == "kie_image":
                # Переключаем на logic создания задачи (аналогично видео), так как старый эндпоинт 404
                # Или пробуем /api/v1/runway/generate для других моделей
                try:
                    payload = {
                        "model": model_cfg['model'],
                        "input": {
                            "prompt": t,
                            "aspect_ratio": "square",
                            "size": "1024x1024"
                        }
                    }
                    r = requests.post("https://api.kie.ai/api/v1/jobs/createTask", 
                                      json=payload, headers={"Authorization": f"Bearer {model_cfg['key']}"}, timeout=60)
                    if r.status_code == 200:
                        res = r.json()
                        task_id = res.get('taskId') or res.get('id') or (res.get('data') or {}).get('taskId')
                        if task_id:
                            # Мини-полинг для картинки (обычно быстрее видео)
                            for _ in range(15):
                                time.sleep(10)
                                pr = requests.get(f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}", 
                                                 headers={"Authorization": f"Bearer {model_cfg['key']}"}, timeout=30)
                                if pr.status_code == 200:
                                    s_data = pr.json().get('data', {})
                                    res_json_str = s_data.get('resultJson', '')
                                    if res_json_str:
                                        res_obj = json.loads(res_json_str)
                                        urls = res_obj.get('resultUrls', [])
                                        if urls:
                                            image_url = urls[0]
                                            break
                except Exception as ex:
                    print(f"⚠️ Kie.ai Image Error: {ex}")

            elif p_type == "laozhang":
                r = requests.post("https://api.laozhang.ai/v1/images/generations",
                                  json={"model": model_cfg['model'], "prompt": t, "n": 1, "size": "1024x1024"},
                                  headers={"Authorization": f"Bearer {model_cfg['key']}", "Content-Type": "application/json"},
                                  timeout=60)
                if r.status_code == 200:
                    image_url = r.json()['data'][0]['url']
                else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")
            elif p_type == "siliconflow":
                r = requests.post("https://api.siliconflow.cn/v1/images/generations", 
                                 json={"model": model_cfg['model'], "prompt": t, "image_size": "1024x1024", "batch_size": 1},
                                 headers={"Authorization": f"Bearer {SILICONFLOW_KEY}", "Content-Type": "application/json"}, timeout=45)
                if r.status_code == 200: 
                    image_url = r.json()['images'][0]['url']
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
                 headers = {"Authorization": f"Bearer {HF_KEY}"}
                 r = requests.post(f"https://router.huggingface.co/hf-inference/models/{model_cfg['model']}", headers=headers, json={"inputs": t}, timeout=60)
                 if r.status_code == 200: image_data = io.BytesIO(r.content)
                 else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

            elif p_type == "cloudflare":
                cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ID}/ai/run/{model_cfg['model']}"
                r = requests.post(cf_url, headers={"Authorization": f"Bearer {CLOUDFLARE_TOKEN}"}, json={"prompt": t}, timeout=60)
                if r.status_code == 200: image_data = io.BytesIO(r.content)
                else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

            elif p_type == "airforce":
                # Using standard OpenAI-like endpoint for Airforce
                url = "https://api.airforce/v1/images/generations"
                r = requests.post(url, json={"model": model_cfg['model'], "prompt": t, "size": "1024x1024"}, timeout=55)
                if r.status_code == 200: image_url = r.json()['data'][0]['url']
                elif r.status_code == 429: print("   ⚠️ Rate Limit (429)")
                else: print(f"⚠️ {p_name} HTTP {r.status_code}: {r.text[:200]}")

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
            print(f"⚠️ {p_name} Error: {e}")
            if 'r' in locals():
                try: print(f"Response: {r.text[:300]}")
                except: pass
            continue

    # --- 4. ШАГ: ОТПРАВКА ---
    if not video_url and not image_url and not image_data: 
        raise Exception("CRITICAL: No Art or Video generated.")
    
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
                # Отправка видео
                bot.send_video(target, video_url, caption=caption, parse_mode='HTML')
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


if __name__ == "__main__":
    run_final()
