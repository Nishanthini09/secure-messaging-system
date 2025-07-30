from flask import Flask, render_template, request, redirect, url_for
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# Load or generate Fernet key
KEY_FILE = "secret.key"

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()

fernet_cipher = Fernet(key)

# In-memory message store
messages = []

# Caesar Cipher function
def caesar_encrypt(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

@app.route('/')
def index():
    return render_template("index.html", messages=messages)

@app.route('/send', methods=['POST'])
def send():
    message = request.form.get('message')
    method = request.form.get('method')
    shift = request.form.get('shift', 0)

    if not method or not message:
        return "Missing message or method", 400

    if method == 'fernet':
        encrypted = fernet_cipher.encrypt(message.encode()).decode()
        messages.append({
            'method': 'Fernet',
            'original': message,
            'encrypted': encrypted,
            'details': 'Fernet encryption with secret.key'
        })
    elif method == 'caesar':
        try:
            shift = int(shift)
            encrypted = caesar_encrypt(message, shift)
            messages.append({
                'method': 'Caesar',
                'original': message,
                'encrypted': encrypted,
                'details': f'Shift: {shift}'
            })
        except ValueError:
            return "Invalid shift value", 400
    else:
        return "Invalid encryption method", 400

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
