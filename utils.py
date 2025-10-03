import requests
import os
import json
import openai
import datetime
import tempfile
import speech_recognition as sr
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydub import AudioSegment

openai.api_key = os.environ.get("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")

# Google Sheets setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

def download_voice(file_id):
    # Step 1: Get file path
    res = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}")
    file_path = res.json()["result"]["file_path"]

    # Step 2: Download voice file
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    ogg_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
    with open(ogg_file.name, 'wb') as f:
        f.write(requests.get(file_url).content)

    # Step 3: Convert OGG to WAV
    wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio = AudioSegment.from_file(ogg_file.name)
    audio.export(wav_file.name, format="wav")

    return wav_file.name

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="ar-EG")
        return text
    except:
        return ""

def extract_expense(text):
    import re
    number_match = re.search(r'\d+', text)
    category = "أخرى"
    if "أكل" in text or "مطعم" in text:
        category = "أكل"
    elif "مواصلات" in text:
        category = "مواصلات"
    elif "كافيه" in text or "قهوة" in text:
        category = "كافيه"

    amount = number_match.group() if number_match else "غير معروف"
    return amount, category

def handle_request(req):
    print("📩 وصل طلب من تليجرام")

    data = req.get_json()
    if "message" not in data or "voice" not in data["message"]:
        return "Not a voice message", 200

    file_id = data["message"]["voice"]["file_id"]
    user = data["message"]["from"]["first_name"]

    # Step 1: Download and convert
    audio_file = download_voice(file_id)

    # Step 2: Transcribe
    text = transcribe_audio(audio_file)
    print("📝 النص المحول:", text)

    # Step 3: Extract data
    amount, category = extract_expense(text)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Step 4: Append to sheet
    sheet.append_row([now, user, amount, category, text])
    print("✅ تم تسجيل المصروف في الشيت")

    return "تم التسجيل", 200
