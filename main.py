from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
import time

app = FastAPI()

# Define your base model for incoming data
class TalkRequest(BaseModel):
    image_url: str
    text: str

# Load environment variables
DID_API_KEY = os.getenv("DID_API_KEY")
if not DID_API_KEY:
    raise Exception("DID_API_KEY environment variable not set")

# Setup HTTP client for asynchronous operations
async with httpx.AsyncClient() as client:
    client.headers["Authorization"] = f"Basic {DID_API_KEY}"

# Endpoint to create and process talk
@app.post("/create-talk")
async def create_talk(talk_request: TalkRequest):
    talk_response = await send_talk_create_request(talk_request.image_url, talk_request.text)
    talk_id = talk_response["id"]
    final_response = await wait_send_talk_get_request(talk_id)
    return final_response

async def send_talk_create_request(image_url: str, text: str):
    """Send a talk request to the d-id/talks API."""
    url = "https://api.d-id.com/talks"  # Adjust the URL based on the actual API endpoint
    request_data = {
        "source_url": image_url,
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "elevenlabs",
                "voice_id": "XTfTIu6Imiu6wQ6T6eZH"
            },
        }
    }
    response = await client.post(url, json=request_data)
    return response.json()

async def wait_send_talk_get_request(talk_id: str):
    """Wait for a talk to be done and then send a GET talk request to the d-id/talks API."""
    url = f"https://api.d-id.com/talks/{talk_id}"
    response = await client.get(url)
    response_data = response.json()
    while response_data["status"] != "done":
        time.sleep(4)  # Sleep for 4 seconds before checking again
        response = await client.get(url)
        response_data = response.json()
    return response_data

