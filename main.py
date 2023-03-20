import json
import os

import openai
import redis
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from gpt_client import GPT

app = FastAPI()
redis = redis.Redis(host="localhost", port=6379)
openai.api_key = os.environ["OPENAI_API_KEY"]


class UserMessage(BaseModel):
    value: str


class File(BaseModel):
    path: str


class SummarizeTarget(BaseModel):
    value: str


SETTING_PROMPT = """わかりやすく答えてください"""

summarize_settings = """
ユーザーから渡される文章の要約をしてください。

要約のフォーマットとしては「タイトル」「本文」「結論」の3つのパートに分けてください。
ただし要約全体で1000字以内に納めてください

それでは文章を渡します。
"""


@app.post("/")
def gpt(use_message: UserMessage):
    print(f"you : {use_message.value}")
    gpt = GPT()
    result = redis.zrange('chat', 0, -1, withscores=True)
    chat_length = len(result)
    # チャット履歴がない場合はChatGPTの振る舞い特性の初期プロンプトを設定する
    if chat_length == 0:
        gpt.add_setting(SETTING_PROMPT)
        redis.zadd("chat", {json.dumps(gpt.latest_system_prompt()): chat_length})

    # チャットの履歴を取得してリクエストに含める
    for elm in result:
        past_message = json.loads(elm[0].decode("utf-8"))
        gpt.add_prompt(past_message)
    # ユーザーの新たな発言をリクエストに含めてリクエストを送る
    response = gpt.add_user_message(use_message.value).request()
    # ユーザーの新たな発言をチャット履歴に保存する
    redis.zadd("chat", {json.dumps(gpt.latest_user_prompt()): chat_length})
    # チャットの返事をチャット履歴に保存する
    redis.zadd("chat", {json.dumps(gpt.latest_assistant_prompt()): chat_length + 1})

    print(f"AI : {response}")
    # チャットの返事をレスポンスボディに入れて返す
    return {"response": response}


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
    gpt = GPT()
    # ChatGPTの振る舞い特性を設定し、要約対象の文章ををリクエストに含めてリクエストを送る
    summary = gpt.add_setting(summarize_settings).add_user_message(target.value).request()
    print(summary)
    # 要約をレスポンスボディに入れて返す
    return {"response": summary}


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
