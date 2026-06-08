"""Vercel serverless entry point for NSACA API."""
from fastapi import FastAPI
from .main import cli

app = FastAPI(title="NSACA API")

@app.get("/")
def root():
    return {"message": "NeuroSymbolic Autonomous Code Architect API", "status": "running"}

@app.get("/status")
def status():
    return {"version": "0.1.0", "model": "gpt-4"}
