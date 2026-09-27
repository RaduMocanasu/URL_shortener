from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import string
import secrets
from database import create_tables, save_url, get_url
from rate_limiter import is_allowed

alphabet = string.ascii_letters + string.digits
shortened_url_length = 6

app = FastAPI()
#static tells fastapi to take the files "as-is", i.e without generating them dynamically, like the database
#whenever the browser requests something under /static/..., look for that file in the frontend folder
#this also handles all possible future frontend files automatically, so there is no need to make @app.get("/script.js") and so on
app.mount("/static", StaticFiles(directory = "frontend"), name = "static")

create_tables()

class URLRequest(BaseModel):
    url : str


@app.get("/")
def home():
    # return {"message": "URL shortener is working"}
    return FileResponse("frontend/index.html")

#posting the url to be shortened
@app.post("/shorten")
def shorten(data: URLRequest, request : Request):

    client_ip = request.client.host

    if not is_allowed(client_ip):
        raise HTTPException(
            status_code = 429, 
            detail = "Too many requests"
        )

    shortened_url = ''.join(secrets.choice(alphabet) for i in range(shortened_url_length))
    save_url(shortened_url, data.url)
    return {
        "original_url" : data.url,
        "shortened_url" : shortened_url
    }

#takes the shortened url and redirects to the actual url
@app.get("/{code}")
def redirect_url(code : str):
    original_url = get_url(code)
    if original_url is None:
        raise HTTPException(status_code = 404, detail = "Short URL not found")

    return RedirectResponse(original_url)
