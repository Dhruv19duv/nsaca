"""Minimal Vercel serverless entry point for NSACA."""
from fastapi import FastAPI

app = FastAPI(title="NSACA API")

@app.get("/")
def root():
    return {"message": "NeuroSymbolic Autonomous Code Architect", "status": "running"}

@app.get("/status")
def status():
    return {"version": "0.1.0", "model": "gpt-4"}
