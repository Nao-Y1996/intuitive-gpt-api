FROM python:3.10.10
# Use python 3.9 or higher

# コンテナ内での作業ディレクトリを設定
WORKDIR /app

# ローカルのrequirements.txtをコンテナ内にコピー
COPY ./container/python/requirements.txt .

# 必要なパッケージをインストール
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV OPENAI_API_KEY "yourKey"

EXPOSE 80

# コンテナ起動時に実行されるコマンドを指定
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]