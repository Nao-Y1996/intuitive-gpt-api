FROM redis:latest

# 必要に応じて、Redisの設定ファイルをコピー
# COPY redis.conf /usr/local/etc/redis/redis.conf

# ポート番号を設定
EXPOSE 6379

# コンテナ起動時に実行されるコマンドを指定（redis serverの起動）
CMD ["redis-server"]