import os
import requests
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\\Program Files\\Tesseract-OCR\\tessdata"

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPEN_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

MODEL_SUMMARY = "meta-llama/llama-3.3-8b-instruct:free"
MODEL_TAGS = "nousresearch/deephermes-3-mistral-24b-preview:free"

def call_openrouter(messages, model):
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300,
    }
    response = requests.post(OPENROUTER_API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

def summarize_text(text: str) -> str:
    prompt = f"Resuma o seguinte texto de forma clara e objetiva:\n\n{text}"
    return call_openrouter([{"role": "user", "content": prompt}], MODEL_SUMMARY)

def extract_tags(text: str) -> list[str]:
    prompt = f"Extraia os principais tópicos e tags deste texto, separados por vírgula:\n\n{text}"
    tags_str = call_openrouter([{"role": "user", "content": prompt}], MODEL_TAGS)
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

def ocr_image(image_path: str) -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='por')
    return text.strip()

def current_timestamp() -> str:
    return datetime.utcnow().isoformat()
