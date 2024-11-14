FROM python:3.9-slim

# 作業ディレクトリを作成
WORKDIR /app

# 必要なライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fletアプリのコードをコピー
COPY . .

# アプリケーションを起動
CMD ["python", "app_main.py"]
