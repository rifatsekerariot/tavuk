FROM python:3.11-slim

WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# FastAPI portunu dışa aç
EXPOSE 8000

# Veritabanını güncelle ve FastAPI uygulamasını başlat
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8000"]
