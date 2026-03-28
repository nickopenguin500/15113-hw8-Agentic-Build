import json
import os
import base64
import tempfile
import shutil
import stat
import errno

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), 'questions.json')
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.dat')


def load_questions():
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['questions']
    except FileNotFoundError:
        print('Error: questions.json not found')
        raise
    except json.JSONDecodeError:
        print('Error: questions.json is not valid JSON')
        raise
    except KeyError:
        print("Error: questions.json missing 'questions' key")
        raise


def read_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'rb') as f:
        data = f.read()
    try:
        decoded = base64.b64decode(data).decode('utf-8')
        return json.loads(decoded)
    except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        # Backup corrupted file for investigation and return empty users dict
        try:
            backup = USERS_FILE + '.corrupt'
            shutil.copy2(USERS_FILE, backup)
            print(f'Warning: users.dat corrupted, backed up to {backup}')
        except Exception:
            print('Warning: users.dat corrupted and could not be backed up')
        return {}


def write_users(users_obj):
    # Serialize and base64 encode to make it non-readable
    raw = json.dumps(users_obj)
    encoded = base64.b64encode(raw.encode('utf-8'))
    # Write to a temporary file then atomically move into place
    dirpath = os.path.dirname(USERS_FILE) or '.'
    fd, tmp_path = tempfile.mkstemp(dir=dirpath)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(encoded)
        # Set file mode to owner read/write only
        try:
            os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass
        os.replace(tmp_path, USERS_FILE)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
