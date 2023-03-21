# useful API for OpenAI API by FastAPI

## What all you need

1. set your OpenAI API key in `docker/python/Dockerfile`
2. run server

      ```commandline
      docker compose up -d
      ```

3. access docs page (http://localhost:8000/docs). Then you can try api. This is running in container.
4. If you want to run in local, you just need to run `python app/main.py` and access another docs page (http://localhost:8080/docs).  
   (You need to run Redis server.)


## System
In order to have continuous conversations with chatgpt's API, it is necessary to create a request containing past dialogues. 
Past dialogues are stored using Redis.

The Redis server and the API server are started up by docker compose.
All settings for the Redis server are default. Please change them if necessary.
The API server is uvicorn and runs inside a Python container.