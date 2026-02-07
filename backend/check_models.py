import os
from dotenv import load_dotenv
import google.generativeai as genai

# load .env
load_dotenv()

# configure gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("\n===== AVAILABLE GEMINI MODELS =====\n")

for model in genai.list_models():
    print(model.name)
