import os
from flask import Flask
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import base64
# Muat environment variables dari file .env
load_dotenv()
import json

# Definisikan objek di luar fungsi agar bisa diimpor oleh file lain
db = None
auth_pyrebase = None

def create_app():
    # Gunakan 'global' untuk memodifikasi variabel yang didefinisikan di luar
    global db, auth_pyrebase

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # --- INISIALISASI FIREBASE ---
    # Hanya inisialisasi jika belum ada instance yang berjalan
    if not firebase_admin._apps:
    # Cek apakah kita di lingkungan Vercel (atau produksi lain)
        cred_base64 = os.getenv('FIREBASE_CREDENTIALS_BASE64')
    if cred_base64:
        # Decode dari Base64
        cred_json_str = base64.b64decode(cred_base64).decode('utf-8')
        cred_json = json.loads(cred_json_str)
        cred = credentials.Certificate(cred_json)
    else:
        # Jika tidak, pakai cara lokal dengan file
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        cred = credentials.Certificate(cred_path)

    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
    })

    # Inisialisasi Pyrebase untuk Autentikasi
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID")
    }
    firebase_pyrebase_app = pyrebase.initialize_app(firebase_config)
    auth_pyrebase = firebase_pyrebase_app.auth()

    # Inisialisasi klien Firestore
    db = firestore.client()

    # --- IMPORT DAN REGISTER BLUEPRINT ---
    # Impor dipindahkan ke dalam fungsi ini untuk menghindari circular import
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin') # Menambahkan prefix /admin

    # (Blueprint lain bisa diregister di sini nanti)
    return app