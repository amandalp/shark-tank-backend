from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import test  # Importing the module we refactored test.py into

app = FastAPI()

# Define a Pydantic model for incoming data
class TalkRequest(BaseModel):
    image_url: str
    text: str
    # audio_url: str

# Add CORS middleware to allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to match the URL of your frontend in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API endpoint to create and process a talk
@app.post("/create-talk")
async def create_talk(request: TalkRequest):
    try:
        # Call the function to create a talk request
        print("main: image url:", request.image_url)
        print("main: text:", request.text)
        create_response = test.send_talk_create_request(request.image_url, request.text)
        print("main: create reponse", create_response)
        talk_id = create_response.get("id")
        print("main: i successfully called send talk create request. talk ID:", talk_id)
        
        if not talk_id:
            return {"error": "Failed to create talk", "details": create_response}
        
        # Wait for the talk to be processed and get the final status
        print("main: now i'm waiting")
        talk_status = test.wait_send_talk_get_request(talk_id)
        print("main: i finished waiting and now i have the status")
        result_url = test.parse_talk_result_url(talk_status)
        print("main: I have hte result url", result_url)
        
        return {"video_url": result_url}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

