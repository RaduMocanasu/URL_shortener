from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import string
import secrets

alphabet = string.ascii_letters + string.digits

app = FastAPI()
shortened_url_length = 6

class URLRequest(BaseModel):
    url : str

urls = {}

@app.get("/")
def home():
    return {"message": "URL shortener is working"}

@app.post("/shorten")
def shorten(data: URLRequest):
    shortened_url = ''.join(secrets.choice(alphabet) for i in range(shortened_url_length))
    urls[shortened_url] = data.url
    return {
        "original_url" : data.url,
        "shortened_url" : shortened_url
    }

@app.get("/{code}")
def redirect_url(code : str):
    if code not in urls:
        raise HTTPException(status_code = 404, detail = "Short URL not found")

    return RedirectResponse(url = urls[code])
