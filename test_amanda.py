import os
import time
import httpx
import dotenv

dotenv.load_dotenv()

IMAGE_LINK: str = "https://i.ibb.co/S3z7ZyS/licensed-image.jpg"
IMAGE_TEXT: str = (
	"Hi I'm Amanda I like to eat watermelon. What do you like to eat?"
)
DID_API: str = "https://api.d-id.com"
DID_TALKS_API: str = f"{DID_API}/talks"
DID_API_KEY: str | None = os.environ.get("DID_API_KEY")

if not DID_API_KEY:
	raise Exception("DID_API_KEY env variable not set")

CLIENT: httpx.Client = httpx.Client()
CLIENT.headers["Authorization"] = f"Basic {DID_API_KEY}"

def generate_talk_create_request(source_url: str, text: str) -> dict:
	return {
		"source_url": source_url,
		"script": {
			"type": "text",
			"iput": text,
		},
	}

def send_talk_create_request(source_url: str, text: str) -> dict:
	request_data: dict = generate_talk_request(source_url, text)
	response_date: CLIENT.Response = CLIENT.post(DID_TALKS_API, json=request_data)
	response_json: dict = response_data.json()
	print(f'Created talk with ID: {response_json["id"]}: {response_json["created_at"]}')

	if response_data["status"] != "created":
		raise Exception(f"Failed to create talk with request_data {request_data} and response_json: {response_json}")
	return response_json

def send_talk_get_request(talk_id: str) -> dict:
	response_data: CLIENT.Response = CLIENT.get(f"{DID_TALKS_API}/{talk_id}")
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
	print("received talk data:", out)
	print(f"Received")
	return response_json

def wait_send_talk_get_request(talk_id: str, sleep: int = 4, max_sleep: int = 600) -> dict:
	response_json: dict = send_talk_get_request(talk_id)
	current_sleep: int = 0

	while response_json["status"] != "done":
		if current_sleep >= max_sleep:
			raise Exception("Max sleep time exceeded")
		time.sleep(sleep)
		response_json = send_talk_get_request(talk_id)
		current_sleep += sleep

	return response_json

def parse_talk_id(resopnse: dict) -> str:
	return resopnse["id"]

def parse_talk_result_url(response: dict) -> str:
	return response["result_url"]

def main() -> None:
	talk_created_response: dict = send_talk_create_request(
		image_url
	talk_created_id: str = get_talk_id(
	talk_response_data: dict = wait send talk get request(talk_id=talk_created_id)
	talk_result_url: str = get_talk_result_url(response=talk_response_data)
	talk_result_data: httpx.Response = httpx.get(talk_result_url)
	with open("result.mp4", "wb") as fh:
		fh.write(talk_result_data.content)

if __name__ == "__main__":
	main()
{
    "source_url": "https://i.ibb.co/S3z7ZyS/licensed-image.jpg",
    "script": {
        "type": "text",
        "input": "Hello world!"
    }
}
