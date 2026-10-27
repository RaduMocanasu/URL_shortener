from fastapi.testclient import TestClient
import rate_limiter
import main
import sqlite3
import database

# TestClient lets python pretend to be a browser/client talking to your FastAPI application
client = TestClient(main.app)

# run all tests with : python -m pytest -v
# run specific test with : python -m pytest tests/test_main.py::test_shorten_valid_url -v

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

def test_redirect_works(monkeypatch):

    # Don't let the real rate limiter interfere with this test
    monkeypatch.setattr(main, "is_allowed", lambda ip: True)        # monkeypatch replaces the actual is_allowed function with a new tiny fake one, which always returns true 

    original_url = "https://example.com/"

    response = client.post(
        "/shorten",
        json={
            "url": original_url
        }
    )

    assert response.status_code == 200
    short_url = response.json()['shortened_url']
    #code = short_url.rsplit('/', 1)[-1]

    response = client.get(
        f"/{short_url}",
        follow_redirects=False  # we want to verify the redirect itself, not the destination
    )

    assert response.status_code in (302, 307)
    assert response.headers['location'] == original_url


def test_unknown_code(monkeypatch):

    # Don't let the real rate limiter interfere with this test
    monkeypatch.setattr(main, "is_allowed", lambda ip: True)        # monkeypatch replaces the actual is_allowed function with a new tiny fake one, which always returns true 

    # Don't write into the real SQLite database
    #monkeypatch.setattr(main, "save_url", lambda code, url: True)

    response = client.get(
        "/hdadhsakjds"
    )

    assert response.status_code == 404


def test_invalid_url(monkeypatch):

    # Don't let the real rate limiter interfere with this test
    monkeypatch.setattr(main, "is_allowed", lambda ip: True)        # monkeypatch replaces the actual is_allowed function with a new tiny fake one, which always returns true 

    # Don't write into the real SQLite database
    monkeypatch.setattr(main, "save_url", lambda code, url: True)

    original_url = "abcdef"

    response = client.post(
        "/shorten",
        json = {
            "url" : original_url
        }
    )

    assert response.status_code == 422


def test_rate_limiting(monkeypatch):

    # Don't write into the real SQLite database
    monkeypatch.setattr(main, "save_url", lambda code, url: True)

    original_url = "https://example.com/"

    for i in range(5):
        response = client.post(
            "/shorten",
            json = {
                "url" : original_url
            }
        )

        assert response.status_code == 200

    response = client.post(
        "/shorten",
        json = {
            "url" : original_url
        }
    )

    assert response.status_code == 429


def test_rate_limiting(monkeypatch):
    current_time = 1000.0

    monkeypatch.setattr(        # simulates time
        rate_limiter.time,
        "monotonic",
        lambda: current_time
    )

    monkeypatch.setattr(rate_limiter, "clients", {})                    # replaces the clients list with a new empty dictionary
    monkeypatch.setattr(rate_limiter, "last_cleanup", current_time)     # replaces the time of the last cleanup with the current time

    ip = "192.168.1.1"

    for _ in range(5):
        assert rate_limiter.is_allowed(ip) is True

    assert rate_limiter.is_allowed(ip) is False



def test_rate_refill(monkeypatch):
    current_time = 1000.0

    monkeypatch.setattr(
        rate_limiter.time,
        "monotonic",
        lambda: current_time
    )

    monkeypatch.setattr(rate_limiter, "clients", {})
    monkeypatch.setattr(rate_limiter, "last_cleanup", current_time)

    ip = "192.168.1.1"

    # Consume all tokens
    for _ in range(5):
        assert rate_limiter.is_allowed(ip) is True

    assert rate_limiter.is_allowed(ip) is False

    # Advance time by 5 seconds
    current_time += 5

    assert rate_limiter.is_allowed(ip) is False

    # Advance another 5 seconds
    current_time += 5

    assert rate_limiter.is_allowed(ip) is True

    # The newly refilled token was consumed
    assert rate_limiter.is_allowed(ip) is False


def test_rate_limiter_cleanup(monkeypatch):

    current_time = 1000.0
    
    monkeypatch.setattr(
        rate_limiter.time,
        "monotonic",
        lambda: current_time
    )

    monkeypatch.setattr(rate_limiter, "clients", {})
    monkeypatch.setattr(rate_limiter, "last_cleanup", current_time)

    old_ip = "192.168.1.1"
    new_ip = "192.168.1.2"

    rate_limiter.is_allowed(old_ip)

    assert old_ip in rate_limiter.clients

    # Simulate 61 seconds passing
    current_time += 61

    # This triggers the automatic cleanup
    rate_limiter.is_allowed(new_ip)

    assert old_ip not in rate_limiter.clients
    assert new_ip in rate_limiter.clients



def test_database_persistence(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"

    # Replaces the database with a new temporary one
    monkeypatch.setattr(database, "get_connection", lambda : sqlite3.connect(db_path))

    database.create_tables()

    original_url = "https://example.com/"
    code = "abc123"

    database.save_url(code, original_url)

    # open url opens another session to retrieve the url
    assert database.get_url(code) == original_url


def test_collision_retry(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    
    # Replaces the database with a new temporary one
    monkeypatch.setattr(database, "get_connection", lambda : sqlite3.connect(db_path))

    database.create_tables()
    
    code = "abc123"

    # First insertion succeeds
    assert database.save_url(
        code,
        "https://example.com/"
    ) is True


    # Second insertion fails
    assert database.save_url(
        code,
        "https://google.com/"
    ) is False

    assert database.get_url(code) == "https://example.com/"
        