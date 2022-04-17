from fastapi.testclient import TestClient

from flashcards_server.app import app


client = TestClient(app)
