from flask import Flask, request
import utils

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    return utils.handle_request(request)
