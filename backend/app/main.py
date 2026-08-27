"""
main.py

This is the FIRST file that runs when you start the backend server.
Its only job is to create the FastAPI "app" object and plug in the
routes (the URLs the frontend can call). Nothing clever happens here
on purpose - that's what app/core/ and app/tools/ are for.

To run this file, from inside backend/:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

app = FastAPI(title="Voice-to-Action Assistant API")


@app.get("/health")
def health_check():
    """
    Health check endpoint to verify that the server is running.
    Returns a simple JSON response indicating the server status.
    """
    return {"status": "ok"}
