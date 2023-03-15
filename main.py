import json

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import os
import openai
import redis

app = FastAPI()
redis = redis.Redis(host="localhost", port=6379)
openai.api_key = os.environ["OPENAI_API_KEY"]


class Prompt(BaseModel):
    value: str


class File(BaseModel):
    path: str


class SummarizeTarget(BaseModel):
    value: str


class Chat(BaseModel):
    messages: list[dict] = []


system_settings = """わかりやすく答えてください"""

summarize_settings = """
ユーザーから渡される文章の要約をしてください。

要約のフォーマットとしては「タイトル」「本文」「結論」の3つのパートに分けてください。
ただし要約全体で1000字以内に納めてください

それでは文章を渡します。
"""


@app.post("/")
def gpt(prompt: Prompt):
    print(f"you : {prompt.value}")
    chat = Chat()
    result = redis.zrange('chat', 0, -1, withscores=True)
    chat_length = len(result)
    # ChatGPTの振る舞い特性を設定する
    if chat_length == 0:
        system = {"role": "system",
                  "content": system_settings}
        chat.messages.append(system)
        redis.zadd("chat", {json.dumps(system): chat_length})

    # チャットの履歴を取得してリクエストに含める
    for elm in result:
        past_message = json.loads(elm[0].decode("utf-8"))
        chat.messages.append(past_message)

    # ユーザーの新たな発言をリクエストに含める
    new_message = {"role": "user",
                   "content": prompt.value}
    chat.messages.append(new_message)

    # ユーザーの新たな発言をチャット履歴に保存する
    redis.zadd("chat", {json.dumps(new_message): chat_length})

    # ChatGPTのAPIにリクエストを送りレスポンスを得る
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat.messages
    )
    # レスポンスからチャットの返事部分を得る
    response_message = {"role": "assistant", "content": res["choices"][0]["message"]["content"]}
    # チャットの返事をチャット履歴に保存する
    redis.zadd("chat", {json.dumps(response_message): chat_length + 1})

    print(f"AI : {response_message['content']}")

    # chat = redis.zrange('chat', 0, -1, withscores=True)

    # チャットの返事をレスポンスボディに入れて返す
    return {"response": response_message}


# chat履歴を削除する
@app.get("/clear")
def clear():
    redis.delete("chat")
    return {"data": f"Chat was cleared."}


@app.post("/transcript")
def transcript(file: File):
    audio_file = open(file.path, "rb")
    transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file, language="ja")
    return {"transcript": transcript["text"]}


@app.post("/summarize")
def summarize(target: SummarizeTarget):
    chat = Chat()
    # ChatGPTの振る舞い特性を設定する
    system = {"role": "system",
              "content": summarize_settings}
    chat.messages.append(system)

    # 要約対象の文章ををリクエストに含める
    new_message = {"role": "user",
                   "content": target.value}
    chat.messages.append(new_message)

    # ChatGPTのAPIにリクエストを送りレスポンスを得る
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat.messages
    )
    # レスポンスからチャットの返事部分を得る
    summary = res["choices"][0]["message"]["content"]
    print(summary)

    # 要約をレスポンスボディに入れて返す
    return {"response": summary}


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
