import google.generativeai as genai
import os

GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_KEY)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")

model = genai.GenerativeModel('gemini-1.5-flash')
try:
    res = model.generate_content("Hi, tell me a joke.")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Gemini 1.5 Flash Error: {e}")

model_pro = genai.GenerativeModel('gemini-pro')
try:
    res = model_pro.generate_content("Hi, tell me a joke.")
    print(f"Gemini Pro Response: {res.text}")
except Exception as e:
    print(f"Gemini Pro Error: {e}")
