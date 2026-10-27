# URL Shortener

A small URL shortener built with FastAPI, SQLite, and a plain HTML/CSS/JavaScript frontend. Submit an HTTP or HTTPS URL to generate a six-character code, then use the short link to redirect to the original address.

## Features

- Browser interface with clickable short links and error messages.
- URL validation through Pydantic.
- Persistent URL storage in SQLite.
- Random, case-sensitive codes containing letters and digits, generated with Python's `secrets` module.
- Collision detection through the database primary key, with up to 10 generation attempts.
- Per-IP rate limiting using an in-memory token bucket.

## Getting started

You need Python with `pip` and `venv`. Run the following commands from the project root.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), enter a URL including `http://` or `https://`, and click **Shorten**. Click the generated link to visit its destination.

The application creates `urls.db` and its table automatically when imported. Start the server from the project root because both the database path and frontend paths are relative to the working directory. The frontend is served by FastAPI and needs no separate build step.

Interactive API documentation is available at [/docs](http://127.0.0.1:8000/docs), with alternative documentation at [/redoc](http://127.0.0.1:8000/redoc).

## API

| Method | Path | Behavior |
| --- | --- | --- |
| `GET` | `/` | Serves the browser interface. |
| `POST` | `/shorten` | Validates and stores a URL, then returns its short code. |
| `GET` | `/{code}` | Redirects to the stored URL with HTTP `307`, or returns `404` if the code is unknown. |

### Create a short link

Send a JSON request to `POST /shorten` with `Content-Type: application/json`:

```json
{
  "url": "https://example.com/"
}
```

Example successful response (`200 OK`; the generated code varies):

```json
{
  "original_url": "https://example.com/",
  "shortened_url": "aB3xY9"
}
```

`shortened_url` contains only the code. Combine it with the server's origin to form a link, such as `http://127.0.0.1:8000/aB3xY9`. Each submission generates a new code, even for a previously shortened URL.

PowerShell example:

```powershell
$result = Invoke-RestMethod -Method Post `
    -Uri 'http://127.0.0.1:8000/shorten' `
    -ContentType 'application/json' `
    -Body '{"url":"https://example.com/"}'
"http://127.0.0.1:8000/$($result.shortened_url)"
```

### Errors

| Status | Meaning |
| --- | --- |
| `404` | The short code does not exist: `Short URL not found`. |
| `422` | The request body is invalid, for example a missing URL or a URL without an HTTP/HTTPS scheme. |
| `429` | The client's rate limit has been reached: `Too many requests`. |
| `500` | All 10 code-generation attempts collided: `Could not generate a unique short URL`. |

## Rate limiting and configuration

Only `POST /shorten` uses the rate limiter. Each client IP starts with 5 tokens, and each allowed request consumes one. Tokens refill at one token every 10 seconds, up to a maximum of 5. Inactive entries are removed after 60 seconds of inactivity during request-triggered cleanup, which runs at most once every 60 seconds.

Configuration currently lives in the source files; there are no application environment variables to set.

| File | Setting | Default |
| --- | --- | --- |
| `main.py` | `shortened_url_length` | `6` characters |
| `main.py` | `n_iter` | `10` attempts |
| `rate_limiter.py` | `capacity` | `5` tokens |
| `rate_limiter.py` | `refill_rate` | `1 / 10` tokens per second |
| `rate_limiter.py` | `inactive_timeout` | `60` seconds |
| `rate_limiter.py` | `cleanup_interval` | `60` seconds |
| `database.py` | Database path in `get_connection()` | `urls.db` |

Rate-limit state is local to each server process and resets on restart. Multiple workers do not share a rate-limit budget. Stored links persist across restarts and have no automatic expiration. Deployment remains a project TODO; `--reload` is intended for local development.

## Tests

Install the test dependencies separately; they are not included in `requirements.txt`:

```bash
python -m pip install pytest httpx
python -m pytest -v
```

The tests cover URL shortening, redirects, unknown codes, invalid URLs, rate limiting and refill, inactive-client cleanup, database persistence, and duplicate-code rejection.

Run tests from the project root. The current suite imports the application, which initializes `urls.db`, and the redirect test writes a URL to that database. Use a separate project copy if you need to keep an existing database untouched.

## Project structure

```text
.
├── main.py              # FastAPI routes, URL validation, and code generation
├── database.py          # SQLite table creation, inserts, and lookups
├── rate_limiter.py      # Per-IP token bucket and inactive-client cleanup
├── requirements.txt     # Pinned application dependencies
├── frontend/
│   ├── index.html       # Browser interface
│   ├── script.js        # API requests and short-link rendering
│   └── style.css        # Interface styling
├── tests/
│   └── test_main.py     # API, database, and rate-limiter tests
└── todo.txt             # Development checklist
```

`urls.db` is generated at runtime and stores the short-code-to-URL mappings.
