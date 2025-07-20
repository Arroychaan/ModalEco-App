from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db, auth_pyrebase
from functools import wraps
import json
from requests.exceptions import HTTPError
from firebase_admin import firestore

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Anda harus login terlebih dahulu.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        try:
            user = auth_pyrebase.create_user_with_email_and_password(email, password)
            auth_pyrebase.send_email_verification(user['idToken'])
            
            user_data = {
                "username": username,
                "email": email,
                "balance": 0.0,
                "is_admin": False,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            db.collection('users').document(user['localId']).set(user_data)
            flash('Akun berhasil dibuat! Cek email untuk verifikasi.', 'success')
            return redirect(url_for('auth.login'))

        # Ganti blok 'except' lama dengan yang ini
        except HTTPError as e:
            # Ubah error dari Firebase menjadi format yang bisa dibaca
            error_json = e.args[1]
            error_data = json.loads(error_json)
            error_message = error_data.get("error", {}).get("message", "UNKNOWN_ERROR")
            
            # Tampilkan pesan error yang lebih spesifik
            flash(f"Gagal membuat akun: {error_message}", 'danger')
            print(f"Firebase Auth Error: {error_message}") # Ini untuk debug di terminal
            return redirect(url_for('auth.register'))
        
        except Exception as e:
            # Penampung untuk error lainnya
            flash(f"Terjadi error yang tidak diketahui: {e}", "danger")
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth_pyrebase.sign_in_with_email_and_password(email, password)
            user_info = auth_pyrebase.get_account_info(user['idToken'])
            email_verified = user_info['users'][0]['emailVerified']
            
            if not email_verified:
                flash('Email Anda belum diverifikasi. Silakan cek inbox.', 'warning')
                return redirect(url_for('auth.login'))

            # Ambil data user dari Firestore
            user_doc_ref = db.collection('users').document(user['localId'])
            user_doc = user_doc_ref.get()
            
            # Simpan info penting di session Flask
            session['user_id'] = user['localId']
            session['id_token'] = user['idToken']
            
            # TAMBAHKAN INI: Simpan status admin di session
            if user_doc.exists and user_doc.to_dict().get('is_admin'):
                session['is_admin'] = True
            else:
                session['is_admin'] = False

            flash('Login berhasil!', 'success')
            
            if session.get('is_admin'):
                 return redirect(url_for('main.dashboard')) # Arahkan ke dashboard utama dulu
            
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            flash('Login gagal. Periksa kembali email dan password Anda.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/logout')
def logout():
    # Hapus session
    session.pop('user_id', None)
    session.pop('id_token', None)
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))