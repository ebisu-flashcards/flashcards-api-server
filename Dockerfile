FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV PORT="8000"
ENV MODULE_NAME="flashcards_server.main"

RUN apt install git

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -e git+https://github.com/ebisu-flashcards/flashcards-core.git#egg=flashcards_core

RUN git clone https://github.com/ebisu-flashcards/flashcards-server.git app
RUN pip install --no-cache-dir -e /app
