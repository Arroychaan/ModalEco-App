from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from . import db
from .auth import login_required
from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_admin import firestore

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    """
    Menampilkan dashboard utama untuk pengguna yang sudah login.
    Mengambil data user, statistik, kontribusi, dan aset yang tersedia.
    """
    try:
        user_id = session['user_id']
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            return redirect(url_for('auth.logout'))
        user_data = user_doc.to_dict()

        # Inisialisasi variabel untuk menghindari error jika data kosong
        my_contributions = []
        total_investment = 0
        
        # Ambil data kontribusi/investasi yang sudah dilakukan user
        contributions_ref = db.collection('contributions').where(filter=FieldFilter('user_id', '==', user_id)).stream()
        for contrib in contributions_ref:
            c_data = contrib.to_dict()
            total_investment += c_data.get('amount_contributed', 0)
            
            # Ambil detail aset untuk setiap kontribusi
            asset_doc = db.collection('assets').document(c_data.get('asset_id', '')).get()
            if asset_doc.exists:
                c_data['asset_name'] = asset_doc.to_dict().get('name', 'N/A')
            else:
                c_data['asset_name'] = 'Aset Telah Dihapus'
            my_contributions.append(c_data)

        # Inisialisasi variabel untuk aset yang tersedia
        available_assets = []
        
        # Ambil aset yang tersedia untuk peluang investasi
        assets_ref = db.collection('assets').order_by('created_at', direction=firestore.Query.DESCENDING).limit(6).stream()
        for doc in assets_ref:
            asset_data = doc.to_dict()
            asset_data['id'] = doc.id  # Menambahkan ID aset, ini penting untuk link
            available_assets.append(asset_data)
        
        # Siapkan data statistik untuk ditampilkan di kartu
        stats = {
            "balance": user_data.get('balance', 0),
            "total_investment": total_investment,
            "asset_count": len(my_contributions)
        }
        
        return render_template('dashboard.html', user=user_data, stats=stats, my_contributions=my_contributions, assets=available_assets)

    except Exception as e:
        print(f"Error di dashboard: {e}") 
        flash('Terjadi kesalahan saat memuat data dashboard.', 'danger')
        return redirect(url_for('auth.login'))


@main.route('/asset/<asset_id>')
@login_required
def asset_detail(asset_id):
    try:
        asset_ref = db.collection('assets').document(asset_id)
        asset_doc = asset_ref.get()
        if not asset_doc.exists:
            flash('Aset investasi tidak ditemukan.', 'danger')
            return redirect(url_for('main.dashboard'))
        asset_data = asset_doc.to_dict()
        asset_data['id'] = asset_doc.id

        # Ambil saldo user yang sedang login
        user_doc = db.collection('users').document(session['user_id']).get()
        user_balance = user_doc.to_dict().get('balance', 0) if user_doc.exists else 0

        if asset_data.get('total_cost', 0) > 0:
            asset_data['progress_percentage'] = (asset_data.get('total_raised', 0) / asset_data['total_cost']) * 100
        else:
            asset_data['progress_percentage'] = 0

        return render_template('asset_detail.html', asset=asset_data, user_balance=user_balance)

    except Exception as e:
        print(f"Error di detail aset: {e}")
        flash('Gagal memuat detail aset.', 'danger')
        return redirect(url_for('main.dashboard'))

@main.route('/contribute/<asset_id>', methods=['POST'])
@login_required
def contribute(asset_id):
    try:
        amount = float(request.form.get('amount'))
        if amount <= 0:
            flash('Jumlah investasi harus lebih dari nol.', 'danger')
            return redirect(url_for('main.asset_detail', asset_id=asset_id))
        
        user_id = session['user_id']
        asset_ref = db.collection('assets').document(asset_id)
        user_ref = db.collection('users').document(user_id)

        @firestore.transactional
        def update_in_transaction(transaction, asset_ref, user_ref, amount):
            asset_snapshot = asset_ref.get(transaction=transaction)
            user_snapshot = user_ref.get(transaction=transaction)

            if not asset_snapshot.exists:
                raise Exception("Aset tidak ditemukan.")
            if not user_snapshot.exists:
                raise Exception("User tidak ditemukan.")

            user_balance = user_snapshot.to_dict().get('balance', 0)
            if user_balance < amount:
                raise Exception(f"Saldo tidak mencukupi. Saldo Anda: Rp{user_balance:,.0f}")

            # --- PERBAIKAN INTI ADA DI SINI ---
            # 1. Hitung saldo baru secara manual
            new_user_balance = user_balance - amount
            # 2. Perintahkan Firestore untuk mengatur saldo menjadi nilai baru
            transaction.update(user_ref, {
                'balance': new_user_balance
            })
            # ------------------------------------

            new_total_raised = asset_snapshot.to_dict().get('total_raised', 0) + amount
            transaction.update(asset_ref, {
                'total_raised': new_total_raised
            })
            
            contribution_ref = db.collection('contributions').document()
            transaction.set(contribution_ref, {
                'user_id': user_id,
                'asset_id': asset_id,
                'amount_contributed': amount,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            return new_total_raised
        
        new_total_raised = update_in_transaction(db.transaction(), asset_ref, user_ref, amount)
        
        all_contributions_ref = db.collection('contributions').where(filter=FieldFilter('asset_id', '==', asset_id)).stream()
        for contrib in all_contributions_ref:
            contrib_data = contrib.to_dict()
            ownership = (contrib_data.get('amount_contributed', 0) / new_total_raised) * 100
            contrib.reference.update({'ownership_percentage': ownership})

        flash(f'Investasi sebesar Rp{amount:,.0f} berhasil! Saldo Anda telah diperbarui.', 'success')
        return redirect(url_for('main.asset_detail', asset_id=asset_id))

    except Exception as e:
        print(f"Error saat kontribusi: {e}")
        flash(f'Gagal melakukan investasi: {e}', 'danger')
        return redirect(url_for('main.asset_detail', asset_id=asset_id))
        # Jalankan transaksi
        new_total_raised = update_in_transaction(db.transaction(), asset_ref, user_id, amount)
        
        # Setelah transaksi sukses, hitung ulang persentase kepemilikan untuk SEMUA kontributor di aset ini
        all_contributions_ref = db.collection('contributions').where(filter=FieldFilter('asset_id', '==', asset_id)).stream()
        for contrib in all_contributions_ref:
            contrib_data = contrib.to_dict()
            ownership = (contrib_data.get('amount_contributed', 0) / new_total_raised) * 100
            contrib.reference.update({'ownership_percentage': ownership})

        flash(f'Investasi sebesar Rp{amount:,.0f} berhasil! Terima kasih atas kontribusimu.', 'success')
        return redirect(url_for('main.asset_detail', asset_id=asset_id))

    except Exception as e:
        print(f"Error saat kontribusi: {e}")
        flash(f'Gagal melakukan investasi: {e}', 'danger')
        return redirect(url_for('main.asset_detail', asset_id=asset_id))