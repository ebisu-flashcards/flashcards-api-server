FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV PORT="8000"
ENV MODULE_NAME="flashcards_server.main"

RUN apt install git
RUN pip install --upgrade pip
RUN pip install git+https://github.com/ebisu-flashcards/flashcards-core.git

RUN git clone https://github.com/ebisu-flashcards/flashcards-server.git ./temp
RUN cp -r ./temp/* /app

RUN pip install /app

RUN pip freeze
