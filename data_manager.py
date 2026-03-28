import json
import os
import base64

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), 'questions.json')
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.dat')


def load_questions():
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)['questions']
    except FileNotFoundError:
        print('Error: questions.json not found')
        raise


def read_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'rb') as f:
        data = f.read()
    try:
        decoded = base64.b64decode(data).decode('utf-8')
        return json.loads(decoded)
    except Exception:
        # If file is corrupted or not decodable, return empty dict
        return {}


def write_users(users_obj):
    # Serialize and base64 encode to make it non-readable
    raw = json.dumps(users_obj)
    encoded = base64.b64encode(raw.encode('utf-8'))
    with open(USERS_FILE, 'wb') as f:
        f.write(encoded)
