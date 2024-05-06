import os
import time
from typing import Optional

import dotenv
import httpx

dotenv.load_dotenv()

IMAGE_LINK: str = "https://storage.googleapis.com/amanda-public-bucket/tim_young.png"
IMAGE_TEXT: str = (
    "hi, i'm tim young from eniac ventures. would love to hear more about your startup."
)
DID_API: str = "https://api.d-id.com"
DID_TALKS_API: str = f"{DID_API}/talks"
DID_API_KEY: Optional[str] = os.environ.get("DID_API_KEY")


if not DID_API_KEY:
    raise Exception("DID_API_KEY environment variable not set")


CLIENT: httpx.Client = httpx.Client()
CLIENT.headers["Authorization"] = f"Basic {DID_API_KEY}"


def generate_talk_create_request(image_url: str, text: str) -> dict:
    """Generate a dictionary for use in a JSON request to the d-id/talks API."""
    return {
        "source_url": image_url,
        "script": {
	    "type": "audio",
	    "audio_url": "https://storage.googleapis.com/amanda-public-bucket/audio.mp3",
	    "provider": {
		"type": "elevenlabs",
            	"voice_id": "YPUnTiFK8hDCl5XNINqt"
	    },
        }
    }

def send_talk_create_request(image_url: str, text: str) -> dict:
    """Send a talk request to the d-id/talks API."""
    request_data: dict = generate_talk_create_request(image_url, text)
    response_data: httpx.Response = CLIENT.post(DID_TALKS_API, json=request_data)
    response_json: dict = response_data.json()
    print("response json", response_json)
    return response_json
    """
    {
        "id": "tlk_TMj4G1wiEGpQrdNFvrqAk",
        "created_at": "2023-03-22T16:38:49.723Z",
        "created_by": "google-oauth2|12345678",
        "status": "created",
        "object": "talk"
    }
    """


def send_talk_get_request(talk_id: str) -> dict:
    """Send a GET talk request to the d-id/talks API."""
    response_data: httpx.Response = CLIENT.get(f"{DID_TALKS_API}/{talk_id}")
    response_json: dict = response_data.json()
    keys: list[str] = [
        "started_at",
        "status",
        "result_url",
        "id",
        "duration",
        "created_at",
    ]
    out: str = ", ".join([f"{k}: {v}" for k, v in response_json.items() if k in keys])
    print("Received talk data:", out)
    return response_json
    """
    {
    "metadata": {
        "driver_url": "bank://lively/driver-02/flipped",
        "mouth_open": false,
        "num_faces": 1,
        "num_frames": 41,
        "processing_fps": 51.51385098457352,
        "resolution": [
            512,
            512
        ],
        "size_kib": 334.22265625
    },
    "audio_url": "https://d-id-talks-prod.s3.us-west-2.amazonaws.com/google-oauth2%12345678/tlk_TMj4G1wiEGpQrdNFvrqAk/microsoft.wav?AWSAccessKeyId=AKIADED3BIK65W6FGA&Expires=167923230&Signature=BpLqGzh83cSL6DSFDSN3BE6pfc2M%3D",
    "created_at": "2023-03-22T16:38:49.723Z",
    "face": {
        "mask_confidence": -1,
        "detection": [
            224,
            198,
            484,
            553
        ],
        "overlap": "no",
        "size": 512,
        "top_left": [
            98,
            119
        ],
        "face_id": 0,
        "detect_confidence": 0.9998300075531006
    },
    "config": {
        "stitch": false,
        "pad_audio": 0,
        "align_driver": true,
        "sharpen": true,
        "auto_match": true,
        "normalization_factor": 1,
        "logo": {
            "url": "ai",
            "position": [
                0,
                0
            ]
        },
        "motion_factor": 1,
        "result_format": ".mp4",
        "fluent": false,
        "align_expand_factor": 0.3
    },
    "source_url": "https://d-id-talks-prod.s3.us-west-2.amazonaws.com/google-oauth2%12345678/tlk_TMj4G1wiEGpQrdNFvrqAk/source/image.jpeg?AWSAccessKeyId=AKIA5CUSDFDF5W6FGA&Expires=167233230&Signature=TtFFRJTg9kEryjaKA7%2BlqPLv98%3D",
    "created_by": "google-oauth2|12345678",
    "status": "done",
    "driver_url": "bank://lively/",
    "modified_at": "2023-03-22T16:39:15.603Z",
    "user_id": "google-oauth2|12345678",
    "result_url": "https://d-id-talks-prod.s3.us-west-2.amazonaws.com/google-oauth2%12345678tlk_TMj4G1wiEGpQrdNFvrqAk/image.mp4?AWSAccessKeyId=AKIA5CUMPWEREWRWW6FGA&Expires=16795234235&Signature=C1lP87Ia1ulFdsddWWEamfZADq2HA%3D",
    "id": "tlk_TMj4G1wiEGpQrdNFvrqAk",
    "duration": 2,
    "started_at": "2023-03-22T16:39:13.633"
}
    we want started_at, status, result_url, id, duration, created_at
    """


def wait_send_talk_get_request(
    talk_id: str, sleep: int = 4, max_sleep: int = 600
) -> dict:
    """Wait for a talk to be done and then send a GET talk request to the d-id/talks API."""
    response_json: dict = send_talk_get_request(talk_id)
    current_sleep: int = 0

    while response_json["status"] != "done":
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


def main() -> None:
    talk_created_response: dict = send_talk_create_request(
        image_url=IMAGE_LINK, text=IMAGE_TEXT
    )
    talk_created_id: str = parse_talk_id(response=talk_created_response)
    talk_response_data: dict = wait_send_talk_get_request(talk_id=talk_created_id)
    talk_result_url: str = parse_talk_result_url(response=talk_response_data)
    talk_result_data: httpx.Response = httpx.get(talk_result_url)
    with open("result.mp4", "wb") as fh:
        fh.write(talk_result_data.content)


if __name__ == "__main__":
    main()
