from fpdf import FPDF
import os
import re

def clean_text(text):
    # Оставляем только буквы, цифры и основные знаки препинания
    # Удаляем все остальное чтобы избежать ошибок рендеринга
    return re.sub(r'[^a-zA-Zа-яА-Я0-9\s.,!?:;\"\'\-\(\)\[\]]', '', text)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Roadmap Playbook', 0, 1, 'R')

pdf = PDF()
pdf.add_page()

# Подключение шрифта (Windows)
font_path = "c:\\Windows\\Fonts\\arial.ttf"
if not os.path.exists(font_path):
    print(f"Font not found at {font_path}")
    exit(1)

# В fpdf2 uni=True больше не нужен, он автоматический для TTF
pdf.add_font('Arial', '', font_path)
pdf.set_font("Arial", size=12)

files = [
    r"c:\Users\андрей\.gemini\antigravity\brain\6c4f5a23-e97a-4bb2-a678-458471c7480a\task.md",
    r"c:\Users\андрей\.gemini\antigravity\brain\6c4f5a23-e97a-4bb2-a678-458471c7480a\implementation_plan.md"
]

pdf.set_font("Arial", size=16)
pdf.cell(0, 10, txt="Roadmap & Implementation Plan (RUS)", ln=1, align='C')
pdf.ln(10)

for fpath in files:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                # Агрессивная очистка
                cleaned = clean_text(line).strip()
                if not cleaned:
                    continue
                
                # Заголовки
                if line.lstrip().startswith("#"):
                    pdf.set_font("Arial", size=14)
                    pdf.ln(5)
                    pdf.multi_cell(0, 10, txt=cleaned, align='L')
                    pdf.set_font("Arial", size=11)
                else:
                    pdf.set_font("Arial", size=11)
                    pdf.multi_cell(0, 6, txt=cleaned, align='L')
        pdf.add_page()

output_path = r"c:\Users\андрей\OneDrive\Desktop\ПРОЕКТЫ\fRieNDLee_FTP\Note\Roadmap_RUS.pdf"
try:
    pdf.output(output_path)
    print(f"SUCCESS: {output_path}")
except Exception as e:
    print(f"ERROR: {e}")
