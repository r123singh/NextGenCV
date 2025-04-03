import os
from dotenv import load_dotenv

load_dotenv()

# Environment configuration
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development') == 'production'

# Firebase configuration
FIREBASE_CONFIG = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    'appId': os.getenv('FIREBASE_APP_ID')
}

# Storage configuration
UPLOAD_FOLDER = 'tmp'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# URLs configuration
if IS_PRODUCTION:
    RESUME_VIEWER_URL = os.getenv('RESUME_VIEWER_URL', 'https://your-firebase-app.web.app/resume-viewer.html')
else:
    RESUME_VIEWER_URL = 'http://127.0.0.1:5500/resume-viewer.html' 