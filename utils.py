import os
from datetime import datetime

def handle_request(req):
    print("Request received!")
    return "OK", 200

def log_to_sheet(date, amount, category, description):
    # Placeholder for Google Sheets integration
    pass
