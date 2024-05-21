import os
import time
from typing import Optional

import dotenv
import httpx
import json
import requests

# Load environment variables
dotenv.load_dotenv()

# Constants for D-ID
DID_API_ENDPOINT = "https://api.d-id.com"
DID_API_KEY: Optional[str] = os.environ.get("DID_API_KEY")

ELEVEN_LABS_API_KEY: Optional[str] = os.environ.get("EL_API_KEY")

# Check API key is set
if not DID_API_KEY:
    raise Exception("DID_API_KEY environment variable not set")

# Setup HTTP client
CLIENT: httpx.Client = httpx.Client()
# CLIENT.headers["Authorization"] = f"Basic {DID_API_KEY}"


def send_talk_create_request(image_url, voice_id, text, api_type):
    external_api_keys = json.dumps({"elevenlabs": ELEVEN_LABS_API_KEY})

    headers_did = {
        "accept": "application/json",
        "x-api-key-external": external_api_keys,
        "content-type": "application/json",
        "authorization": f"Basic {DID_API_KEY}",
    }

    headers_elevenlabs = {
        #Not sure I need this accept header?
        #"Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": f"Basic {EL_API_KEY}",
    }

    if api_type == 'd-id':
        data = {
            "script": {
                # "type": "audio",
                # "audio_url": "https://storage.googleapis.com/amanda-public-bucket/audio.mp3"
                "type": "text", 
                "input": text, 
                "provider": {"type": "elevenlabs", "voice_id": voice_id}
            },
            "source_url": image_url,
        }
        response = requests.post(f"{DID_API_ENDPOINT}/talks", json=data, headers=headers_did)
        print("Response from openai API:", response.text)
    elif api_type == 'elevenlabs':
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        response = requests.post("https://api.elevenlabs.io/v1/text-to-speech/voice_id/stream", json=data, headers=headers_elevenlabs)
        print("Response from elevenlabs API:", response.text)

    return response.json()


    # this is what the response should look like:
    """
    {
        "id": "tlk_K26q74SMAbZjL-F3RwvdG",
        "created_at": "2024-05-14T02:21:58.595Z",
        "created_by": "google-oauth2|113929601480866265062",
        "status": "created",
        "object": "talk"
    }
    """

    # response = httpx.post(DID_TALKS_URL, json=data, headers=headers)
    response = requests.post(f"{DID_API_ENDPOINT}/talks", json=data, headers=headers)

    print("test.py: response timed after post", response)
    print("test.py: send talk create request: i successfully sent a call to d-id")
    print("test.py: response.text", response.text)

    return response.json()


def send_talk_get_request(talk_id: str) -> dict:
    url = f"{DID_API_ENDPOINT}/talks/{talk_id}"
    get_headers = {
        "accept": "application/json",
        "authorization": f"Basic {DID_API_KEY}",
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


def wait_send_talk_get_request(
    talk_id: str, sleep: int = 4, max_sleep: int = 600
) -> dict:
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


# def main(image_url, text):
#     response = send_talk_create_request(image_url, text)
#     print("Response from D-ID API:", response)


# Main function only for direct script execution, not when imported
# if __name__ == "__main__":
#     # Example usage
#     # resp = send_talk_create_request(IMAGE_URL, "https://storage.googleapis.com/amanda-public-bucket/audio.mp3")
#     example_text = "Some text"
#     main(IMAGE_URL, example_text)


def main() -> None:
    # Constants for D-ID inputs
    # TODO: generate speech text
    image_url = "https://storage.googleapis.com/amanda-public-bucket/tim_young.png"
    image_text: str = (
        "hi, i'm tim young from eniac ventures. would love to hear more about your startup."
    )

    # Constants for Eleven Labs
    # TODO: get correct voice ID for VC
    voice_id: str = "YPUnTiFK8hDCl5XNINqt"

    talk_created_response: dict = send_talk_create_request(
        image_url=image_url, voice_id=voice_id, text=image_text
    )
    talk_created_id: str = parse_talk_id(response=talk_created_response)
    talk_response_data: dict = wait_send_talk_get_request(talk_id=talk_created_id)
    talk_result_url: str = parse_talk_result_url(response=talk_response_data)
    talk_result_data: httpx.Response = httpx.get(talk_result_url)

    with open("result.mp4", "wb") as fh:
        fh.write(talk_result_data.content)


if __name__ == "__main__":
    main()
