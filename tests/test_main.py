from fastapi.testclient import TestClient
import main

# TestClient lets python pretend to be a browser/client talking to your FastAPI application
client = TestClient(main.app)

def test_shorten_valid_url(monkeypatch):

    # Don't let the real rate limiter interfere with this test
    monkeypatch.setattr(main, "is_allowed", lambda ip: True)        # monkeypatch replaces the actual is_allowed function with a new tiny fake one, which always returns true 

    # Don't write into the real SQLite database
    monkeypatch.setattr(main, "save_url", lambda code, url: True)

    response = client.post(
        "/shorten",
        json={
            "url": "https://example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "shortened_url" in data
    assert len(data["shortened_url"]) == 6


