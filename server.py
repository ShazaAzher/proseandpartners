from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
import os

# =====================
# CONFIG
# =====================
JWT_SECRET = "SUPER_SHARED_SECRET"
JWT_ALGO = "HS256"
TOKEN_TTL_MIN = 30
DAILY_BUDGET = 10.0

WORKFLOW_LIMITS = {
    "supir": 6,
    "skin": 80,
    "relight": 80
}

BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = BASE_DIR  # HTML files are in the same folder

# =====================
# USERS
# =====================
USERS = {
    "proseandpartners@gmail.com": "admin123"
}

# =====================
# MODELS
# =====================
class LoginRequest(BaseModel):
    username: str
    password: str

# =====================
# APP
# =====================
app = FastAPI(title="Prose & Partners Gateway")

# ✅ Serve static files correctly
# Directory is just "static" inside BASE_DIR
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# =====================
# TOKEN HELPERS
# =====================
def issue_token(username: str):
    payload = {
        "user": username,
        "budget": {
            "daily_limit": DAILY_BUDGET,
            "remaining": DAILY_BUDGET
        },
        "usage": {
            "supir": 0,
            "skin": 0,
            "relight": 0
        },
        "limits": WORKFLOW_LIMITS,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MIN)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

# =====================
# API ROUTES
# =====================
@app.post("/login")
def login(data: LoginRequest):
    if USERS.get(data.username) != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = issue_token(data.username)
    return {"token": token}

# =====================
# FRONTEND ROUTES
# =====================
@app.get("/")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/menu")
def serve_menu():
    return FileResponse(os.path.join(FRONTEND_DIR, "menu.html"))
