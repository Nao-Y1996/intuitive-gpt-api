# useful API for OpenAI API by FastAPI

## What all you need

1. set your OpenAI API key in `docker/python/Dockerfile`
2. run server

      ```commandline
      docker compose up -d
      ```

3. access docs page (http://localhost:8000/docs). Then you can try api. This is running in container.
4. If you want to run in local, you just need to run `python main.py`. and access another docs page (http://localhost:8080/docs)