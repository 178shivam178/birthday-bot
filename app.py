import os
import logging
from datetime import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import openai

# Flask & SocketIO Setup
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_KEY")

# Logging setup
logging.basicConfig(
    filename='logs/messages.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def get_gpt_response(user_input):
    """
    Gets a fast GPT response for birthday chatbot logic.
    """
    prompt = f"""
    You are a chatbot for wishing Anushka Singh happy birthday.
    
    Rules:
    1. If user's first input has any words, ask: "Are you Anushka Singh?"
    2. If user says "Yes", "Haan", "Haa", any case reply with one of:
       - "Happy Birthday, Bsdk"
    3. If user says "No", reply: "maderchod apna kaam kr na mujhe kyu disturb kr rha."
    4. If user greets ("Hi", "Hello", etc.), restart and ask: "Are you Anushka Singh?"
    
    User Input: {user_input}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # faster than full GPT-4
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=80,
        temperature=0.7
    )

    return response.choices[0].message["content"].strip()

def log_message(user_message, bot_response, ip_address):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"Timestamp: {timestamp} - IP: {ip_address} - User: {user_message} - Bot: {bot_response}"
    logging.info(log_entry)

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    ip_address = request.remote_addr
    response = get_gpt_response(msg)
    emit('response', response)
    log_message(msg, response, ip_address)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8501)
