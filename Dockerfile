FROM python:3.9

WORKDIR /flashcards

RUN apt install git
RUN pip install --upgrade pip

COPY ./flashcards_server /flashcards/flashcards_server
COPY ./setup.cfg         /flashcards/flashcards_server
COPY ./pyproject.toml    /flashcards/flashcards_server

RUN pip install --no-cache-dir --upgrade /flashcards/flashcards_server

CMD ["uvicorn", "flashcards_server.app:app", "--host", "0.0.0.0", "--port", "80"]
