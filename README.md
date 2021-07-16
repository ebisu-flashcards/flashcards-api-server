# Flashcards API - WIP

[![Unit Tests](https://github.com/ebisu-flashcards/flashcards-api/actions/workflows/tests.yml/badge.svg)](https://github.com/ebisu-flashcards/flashcards-api/actions/workflows/tests.yml)  [![Coverage Status](https://coveralls.io/repos/github/ebisu-flashcards/flashcards-api/badge.svg)](https://coveralls.io/github/ebisu-flashcards/flashcards-api)  [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)   <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

Flashcards REST API.

**NOTE**: This is a work-in-progress, not running application. 
Do not expect it to just download it and be able to run it if you're not
familiar with Python.

## Setup development server

```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install .

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
