import os
import time
from typing import Optional

import dotenv
import httpx
import json
import urllib.parse
import requests

# Load environment variables
dotenv.load_dotenv()

# Constants for D-ID
DID_TALKS_URL: str = "https://api.d-id.com/talks"
DID_API_KEY: Optional[str] = os.environ.get("DID_API_KEY")

# Constants for D-ID inputs
IMAGE_URL: str = "https://storage.googleapis.com/amanda-public-bucket/tim_young.png"
IMAGE_TEXT: str = "hi, i'm tim young from eniac ventures. would love to hear more about your startup."

# Constants for Eleven Labs
ELEVEN_LABS_API_KEY: Optional[str] = os.environ.get("EL_API_KEY")
VOICE_ID: str = "YPUnTiFK8hDCl5XNINqt"

# Check API key is set
if not DID_API_KEY:
    raise Exception("DID_API_KEY environment variable not set")

# Setup HTTP client
CLIENT: httpx.Client = httpx.Client()
#CLIENT.headers["Authorization"] = f"Basic {DID_API_KEY}"

def send_talk_create_request(image_url, text):
    print("test.py: EL api key", ELEVEN_LABS_API_KEY)
    print("test.py: did api key", DID_API_KEY)
    external_api_keys = json.dumps({"elevenlabs": ELEVEN_LABS_API_KEY})
    #external_api_keys_encoded = urllib.parse.quote(external_api_keys)

    headers = {
        "accept": "application/json",
        "x-api-key-external": "{\"elevenlabs\": \"3d4e59e1b27a2e2d5215405ee6d6109e\"}",
        "content-type": "application/json",
        "authorization": "Basic WVcxaGJtUmhiR1ZwWjJod1FHZHRZV2xzTG1OdmJROmZmWktGR2pVM2VDWGl6S2V1OHdHMQ=="
        #'Authorization': f'Basic {DID_API_KEY}',  # Use Basic Auth for D-ID
        #'x-api-key-external': external_api_keys,  # URL encoded JSON
        #'Content-Type': 'application/json'
    }

    data = {
        "script": {
            #"type": "audio",
	        #"audio_url": "https://storage.googleapis.com/amanda-public-bucket/audio.mp3"
            "type": "text",
            "input": text,
            "provider": {
                "type": "elevenlabs",
                "voice_id": "YPUnTiFK8hDCl5XNINqt"
            }
        },
        "source_url": image_url
    }
    
    #this is what the response should look like:
    """
    {
        "id": "tlk_K26q74SMAbZjL-F3RwvdG",
        "created_at": "2024-05-14T02:21:58.595Z",
        "created_by": "google-oauth2|113929601480866265062",
        "status": "created",
        "object": "talk"
    }
    """

    print("did url", DID_TALKS_URL)
    print("json data", data)
    print("headers", headers)


    #response = httpx.post(DID_TALKS_URL, json=data, headers=headers)
    response = requests.post(DID_TALKS_URL, json=data, headers=headers)
    print("test.py: response immed after post", response)
    response_data = response.json()
    print("test.py: send talk create request: i successfully sent a call to d-id")
    print("test.py: response.text", response.text)
    return response.json()

def send_talk_get_request(talk_id: str) -> dict:
    #response_data: httpx.Response = CLIENT.get(f"{DID_TALKS_URL}/{talk_id}")
    #response_json: dict = response_data.json()


    url = 'https://api.d-id.com/talks/(f"{talk_id}")'
    get_headers = {
        "accept": "application/json",
        "authorization": "Basic WVcxaGJtUmhiR1ZwWjJod1FHZHRZV2xzTG1OdmJROmZmWktGR2pVM2VDWGl6S2V1OHdHMQ=="
    }

    response = requests.get(url, headers=get_headers)
    print("test.py: get talk request url", url)
    response_json: dict = response.json()

    keys: list[str] = [
        "started_at",
        "status",
        "result_url",
        "id",
        "duration",
        "created_at",
    ]
    out: str = ", ".join([f"{k}: {v}" for k, v in response_json.items() if k in keys])
    print("test.py: Received talk data:", response_json)
    return response_json

def wait_send_talk_get_request(talk_id: str, sleep: int = 4, max_sleep: int = 600) -> dict:
    response_json: dict = send_talk_get_request(talk_id)

    current_sleep: int = 0

    while response_json["status"] != "done":
        print("test.py: in the wait send talk get request while loop")
        if current_sleep >= max_sleep:
            raise Exception("Max sleep time exceeded")
        time.sleep(sleep)
        response_json = send_talk_get_request(talk_id)
        current_sleep += sleep

    return response_json

def parse_talk_id(response: dict) -> str:
    """Get the talk ID from a response to a talk request."""
    return response["id"]

def parse_talk_result_url(response: dict) -> str:
    """Get the talk result URL from a response to a talk request."""
    return response["result_url"]

def main (image_url, text):
    response = send_talk_create_request(image_url, text)
    print("Response from D-ID API:", response)

# Main function only for direct script execution, not when imported
if __name__ == "__main__":
    # Example usage
    #resp = send_talk_create_request(IMAGE_URL, "https://storage.googleapis.com/amanda-public-bucket/audio.mp3")
    example_text = "Some text"
    main(IMAGE_URL, example_text)
    print(resp)

"""
def main() -> None:
    talk_created_response: dict = send_talk_create_request(
        image_url=IMAGE_URL, text=IMAGE_TEXT
    )
    talk_created_id: str = parse_talk_id(response=talk_created_response)
    talk_response_data: dict = wait_send_talk_get_request(talk_id=talk_created_id)
    talk_result_url: str = parse_talk_result_url(response=talk_response_data)
    talk_result_data: httpx.Response = httpx.get(talk_result_url)
    with open("result.mp4", "wb") as fh:
        fh.write(talk_result_data.content)


if __name__ == "__main__":
    main()
"""
