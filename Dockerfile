# Dockerfile

# Gunakan base image Python yang ringan
FROM python:3.10-slim

# Atur direktori kerja di dalam kontainer
WORKDIR /app

# Salin file requirements dan install library
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode aplikasi ke dalam kontainer
COPY . .

# Perintahkan Gunicorn untuk menjalankan aplikasi kita
# Ini akan menjalankan fungsi create_app() dari file run.py
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app"]