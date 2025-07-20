import os
from flask import Flask
from threading import Thread
import requests
import time

port = os.environ.get('PORT')

app = Flask(__name__)

URL = " "  # Replace with your render URL

@app.route('/')
def index():
    return "Alive"

def run():
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

def request_url_every_minute():
    while True:
        try:
            response = requests.get(URL)
            print(f"keep_alive.py => Status Code: {response.status_code}")
            # Process the response if needed
            # For example, print the content: print(response.content)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

        # Wait for 1 minute
        time.sleep(60)

def start_requesting():
    t = Thread(target=request_url_every_minute)
    t.start()