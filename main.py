from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    print("✅ Voice message received!")
    return "OK", 200
