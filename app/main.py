import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.api import run_brief, auth
from app.core.database import engine, Base

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aevel HQ")

# CORS (Allow all for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware (Required for Google OAuth)
# 'AEVEL_SECRET' should be in env, defaulting to a random string for dev
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev_secret_key_123"))

# API Routes
app.include_router(run_brief.router, prefix="/api")
app.include_router(auth.router, prefix="/auth")

# Static Files (Frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
