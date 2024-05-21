import os
import dotenv
from typing import Optional
from fastapi import FastAPI, HTTPException, Body, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import test  # Importing the module we refactored test.py into

# Load environment variables
dotenv.load_dotenv()

app = FastAPI()

# Define a Pydantic model for incoming data
class TalkRequest(BaseModel):
    image_url: str
    text: str
    voice_id: str #eleven labs individual voice id
    api_type: str #'d-id' or 'elevenlabs'
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
        print("main: API type:", request.api_type)
        print("main: image url:", request.image_url)
        print("main: text:", request.text)
        print("main: voice id:", request.voice_id)
        create_response = test.send_talk_create_request(request.image_url, request.voice_id, request.text, api_type=request.api_type)
        #print("main: create reponse", create_response)

        if request.api_type == "elevenlabs":
            if create_response:
                return StreamingResponse(create_response, media_type="audio/mp3")
            else:
                raise HTTPException(status_code=500, detail="Failed to stream audio")

        ###
        #TODO: Add response handling for elevenlabs, not really sure what the response body is
        #TODO: Also not sure if i should use the TTS endpoint or the streaming endpoint
        #TTS endpoint: https://api.elevenlabs.io/v1/text-to-speech/voice_id
        #Streaming endpoint: https://api.elevenlabs.io/v1/text-to-speech/voice_id/stream
        ###

        # response handling for d-id
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

