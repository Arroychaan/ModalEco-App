# ModalEco

**Investasi Berdampak, Dimulai dari Komunitas.**

![Screenshot Dashboard ModalEco](https://via.placeholder.com/800x450.png?text=Screenshot+Aplikasi+ModalEco)

## 📝 Deskripsi

**ModalEco** adalah prototipe platform web *fintech* sosial yang memungkinkan sebuah komunitas untuk melakukan investasi patungan pada aset-aset ramah lingkungan. Aplikasi ini dibangun untuk mendemonstrasikan konsep *crowdfunding* skala mikro untuk tujuan keberlanjutan (sustainability), di mana setiap anggota dapat berkontribusi sesuai kemampuan dan mendapatkan imbal hasil (ROI) secara proporsional.

Platform ini memfasilitasi seluruh alur, mulai dari pendaftaran pengguna dengan verifikasi email, penambahan aset oleh admin, hingga proses investasi oleh pengguna yang terintegrasi dengan sistem saldo virtual.

---

## ✨ Fitur Utama

* **Autentikasi Pengguna:** Sistem pendaftaran dan login yang aman menggunakan Firebase Authentication, lengkap dengan verifikasi email otomatis.
* **Manajemen Role:** Pembagian hak akses antara **User** (investor) dan **Admin** (pengelola aset).
* **Dashboard Interaktif:** Tampilan ringkasan performa investasi, saldo, dan daftar peluang investasi baru.
* **Sistem Saldo Virtual:** Setiap pengguna memiliki saldo internal yang dapat digunakan untuk berinvestasi.
* **Panel Admin:** Halaman khusus bagi admin untuk menambah dan mengelola aset investasi yang akan ditawarkan kepada pengguna.
* **Logika Investasi Transaksional:** Proses investasi yang aman, memastikan saldo pengguna berkurang dan dana aset bertambah dalam satu operasi yang konsisten (menggunakan Firestore Transaction).

---

## 🛠️ Teknologi yang Digunakan

* **Backend:** Flask (Python)
* **Database:** Google Firestore (NoSQL)
* **Autentikasi:** Firebase Authentication
* **Deployment:** Vercel
* **Frontend:** HTML, Bootstrap 5, Jinja2

---

## 🚀 Cara Instalasi & Menjalankan Lokal

Untuk menjalankan proyek ini di lingkungan lokal, ikuti langkah-langkah berikut:

1.  **Clone repository ini:**
    ```bash
    git clone [URL_REPOSITORY_KAMU]
    cd ModalEco
    ```

2.  **Buat dan aktifkan virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install semua library yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Siapkan file Environment & Kredensial:**
    * Buat file `.env` di direktori utama dan isi sesuai dengan contoh di bawah, menggunakan kredensial Firebase-mu.
    * Letakkan file `firebase-credentials.json` (kunci admin) di direktori utama.

    **Contoh `.env`:**
    ```env
    SECRET_KEY="KUNCI_RAHASIA_SUPER_ACAK"
    FIREBASE_CREDENTIALS_PATH="firebase-credentials.json"
    FIREBASE_DATABASE_URL="..."
    FIREBASE_API_KEY="..."
    FIREBASE_AUTH_DOMAIN="..."
    FIREBASE_PROJECT_ID="..."
    FIREBASE_STORAGE_BUCKET="..."
    FIREBASE_MESSAGING_SENDER_ID="..."
    FIREBASE_APP_ID="..."
    ```

5.  **Jalankan aplikasi:**
    ```bash
    flask run
    ```
    Aplikasi akan berjalan di `http://127.0.0.1:5000`.

---

##  STATUS

Proyek ini sedang dalam tahap pengembangan aktif.