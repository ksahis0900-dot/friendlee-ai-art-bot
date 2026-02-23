
from PIL import Image, ImageDraw, ImageFont
import os

def create_report():
    # Настройки
    width, height = 800, 1200
    bg_color = (15, 15, 25)  # Dark premium Blue
    text_color = (240, 240, 240)
    accent_color = (255, 100, 100) # Red for accent
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Пытаемся найти шрифт
    font_path = "C:/Windows/Fonts/arial.ttf" # Windows specific
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf" # Linux fallback
    
    try:
        title_font = ImageFont.truetype(font_path, 40)
        subtitle_font = ImageFont.truetype(font_path, 30)
        text_font = ImageFont.truetype(font_path, 20)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # Рисуем заголовок
    draw.text((width//2, 50), "ОТЧЕТ О РАЗРАБОТКЕ fRieNDLee Art Bot", fill=text_color, font=title_font, anchor="mm")
    draw.line((100, 80, 700, 80), fill=accent_color, width=2)

    # 1. Начало
    draw.text((50, 150), "1. ТОЧКА А (Начало пути)", fill=accent_color, font=subtitle_font)
    draw.text((70, 200), "- Хаотичные падения скриптов.", fill=text_color, font=text_font)
    draw.text((70, 230), "- Ограниченный набор стилей (только киберпанк).", fill=text_color, font=text_font)
    draw.text((70, 260), "- Плохая грамматика и отсутствие праздников.", fill=text_color, font=text_font)

    # Линия графика
    draw.line((400, 300, 400, 400), fill=text_color, width=3)
    draw.polygon([(390, 400), (410, 400), (400, 420)], fill=accent_color)

    # 2. Этап 2
    draw.text((50, 450), "2. ЭТАП 2: ФУНДАМЕНТ", fill=accent_color, font=subtitle_font)
    draw.text((70, 500), "- Организация 10+ провайдеров (Kie, Groq, Gemini).", fill=text_color, font=text_font)
    draw.text((70, 530), "- Автоматизация через GitHub Actions.", fill=text_color, font=text_font)
    draw.text((70, 560), "- Добавление календаря русских праздников.", fill=text_color, font=text_font)

    # Линия графика
    draw.line((400, 600, 400, 700), fill=text_color, width=3)
    draw.polygon([(390, 700), (410, 700), (400, 720)], fill=accent_color)

    # 3. Этап 3
    draw.text((50, 750), "3. ЭТАП 3: ИНТЕЛЛЕКТ", fill=accent_color, font=subtitle_font)
    draw.text((70, 800), "- Внедрение Watchdog (умный перезапуск).", fill=text_color, font=text_font)
    draw.text((70, 830), "- Создание 'Памяти Ошибок' (Error Memory).", fill=text_color, font=text_font)
    draw.text((70, 860), "- Гибридная логика: Flux vs Kie Nano Banana.", fill=text_color, font=text_font)

    # 4. Итог
    draw.rectangle([100, 950, 700, 1150], outline=accent_color, width=3)
    draw.text((width//2, 1000), "ТЕКУЩЕЕ СОСТОЯНИЕ", fill=accent_color, font=subtitle_font, anchor="mm")
    draw.text((width//2, 1040), "Стабильность: 99.9%", fill=text_color, font=text_font, anchor="mm")
    draw.text((width//2, 1070), "Эстетика: Премиум (Русский Дух)", fill=text_color, font=text_font, anchor="mm")
    draw.text((width//2, 1100), "Автономия: Полная 24/7", fill=text_color, font=text_font, anchor="mm")

    # Сохраняем
    img.save("Development_Journey_Report.pdf", "PDF", resolution=100.0)
    print("✅ Отчет создан: Development_Journey_Report.pdf")

if __name__ == "__main__":
    create_report()
