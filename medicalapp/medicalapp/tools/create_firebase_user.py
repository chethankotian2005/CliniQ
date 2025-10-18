import sys
import json
import argparse
import time
import secrets
import string

parser = argparse.ArgumentParser()
parser.add_argument('--email', help='Email for the new user')
parser.add_argument('--password', help='Password for the new user')
args = parser.parse_args()

def generate_email():
    ts = int(time.time())
    return f'demo_user_{ts}@example.com'

def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

email = args.email or generate_email()
password = args.password or generate_password()

try:
    import firebase_admin
    from firebase_admin import auth, credentials
except Exception as e:
    print(json.dumps({'ok': False, 'error': f'Failed to import firebase_admin: {e}'}))
    sys.exit(1)

try:
    # initialize if not already
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
except Exception as e:
    # try initialize without explicit args (rely on env var), or report error
    try:
        firebase_admin.initialize_app()
    except Exception as e2:
        print(json.dumps({'ok': False, 'error': f'Failed to initialize Firebase Admin SDK: {e2}'}))
        sys.exit(1)

try:
    user = auth.create_user(email=email, password=password)
    print(json.dumps({'ok': True, 'uid': user.uid, 'email': email, 'password': password}))
except Exception as e:
    print(json.dumps({'ok': False, 'error': str(e)}))
    sys.exit(1)
