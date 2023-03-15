FROM python:3.10.10

# コンテナ内での作業ディレクトリを設定
WORKDIR /app

# ローカルのrequirements.txtをコンテナ内にコピー
COPY ./docker/python/requirements.txt .

# 必要なパッケージをインストール
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY ./main.py .

ENV OPENAI_API_KEY "yourKey"

EXPOSE 80

# コンテナ起動時に実行されるコマンドを指定
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]