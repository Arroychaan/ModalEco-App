from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from functools import wraps
from . import db
from firebase_admin import firestore

admin = Blueprint('admin', __name__)

# Decorator baru khusus untuk halaman admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Cek apakah user login DAN status admin-nya True
        if not session.get('is_admin'):
            flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/dashboard')
@admin_required
def dashboard():
    # Ambil semua aset dari Firestore untuk ditampilkan
    assets_ref = db.collection('assets').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
    assets = []
    for asset in assets_ref:
        asset_data = asset.to_dict()
        asset_data['id'] = asset.id
        assets.append(asset_data)
        
    return render_template('admin_dashboard.html', assets=assets)


@admin.route('/asset/new', methods=['GET', 'POST'])
@admin_required
def create_asset():
    if request.method == 'POST':
        try:
            asset_data = {
                "name": request.form.get('name'),
                "description": request.form.get('description'),
                "total_cost": float(request.form.get('total_cost')),
                "total_raised": 0.0,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            # Tambahkan data aset baru ke koleksi 'assets'
            db.collection('assets').add(asset_data)
            flash('Aset investasi baru berhasil dibuat!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'Gagal membuat aset: {e}', 'danger')
            return redirect(url_for('admin.create_asset'))
            
    return render_template('create_asset.html')