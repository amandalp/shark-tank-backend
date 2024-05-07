from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import test  # Importing the module we refactored test.py into

app = FastAPI()

# Define a Pydantic model for incoming data
class TalkRequest(BaseModel):
    image_url: str
    audio_url: str

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
        create_response = test.send_talk_create_request(request.image_url, request.audio_url)
        talk_id = create_response.get("id")
        
        if not talk_id:
            return {"error": "Failed to create talk", "details": create_response}
        
        # Wait for the talk to be processed and get the final status
        talk_status = test.wait_send_talk_get_request(talk_id)
        result_url = test.parse_talk_result_url(talk_status)
        
        return {"video_url": result_url}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

