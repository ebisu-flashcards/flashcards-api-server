from conftest import client
import flashcards_core


def test_endpoints_are_protected():
    assert 401 == client.get("/algorithms").status_code


def test_get_algorithms(monkeypatch, auth):
    fake_algorithms = ["test_alg_1", "test_alg_2"]
    monkeypatch.setattr(flashcards_core.schedulers, "SCHEDULERS", fake_algorithms)

    response = client.get("/algorithms")
    assert response.status_code == 200
    assert response.json() == fake_algorithms
