# Flashcards API Server - WIP

[![Unit Tests](https://github.com/ebisu-flashcards/flashcards-api/actions/workflows/tests.yml/badge.svg)](https://github.com/ebisu-flashcards/flashcards-api/actions/workflows/tests.yml)  [![Coverage Status](https://coveralls.io/repos/github/ebisu-flashcards/flashcards-api/badge.svg)](https://coveralls.io/github/ebisu-flashcards/flashcards-api)   [![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)   [![Code on: GitHub](https://img.shields.io/badge/Code%20on-GitHub-blueviolet)](https://github.com/ebisu-flashcards/flashcards-server)    [![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Flashcards REST API server.

**NOTE**: This is a work-in-progress, not running application. 
Do not expect it to just download it and be able to run it if you're not
familiar with Python.

## Setup development server

```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install -e git+https://github.com/ebisu-flashcards/flashcards-server.git#egg=flashcards_server
> pip install -e .

[ ... pip logs ... ]

> uvicorn flashcards_api.main:app

INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:60494 - "GET / HTTP/1.1" 200 OK
```

## OpenAPI Docs

Visit either `127.0.0.1:8000/docs` or `127.0.0.1:8000/redoc`.

You can also see the API docs at https://ebisu-flashcards.github.io/flashcards-api/redoc.


# Contribute

```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install -e .
> pre-commit install

... do some changes ...

> pytest
```
The pre-commit hook runs Black and Flake8 with fairly standard setups. Do not send a PR if these checks, or the tests, are failing.
