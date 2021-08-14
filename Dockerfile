FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV PORT="8000"

COPY . /app

RUN apt install git

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -e git+https://github.com/ebisu-flashcards/flashcards-core.git#egg=flashcards_core
RUN pip install --no-cache-dir -e /app
