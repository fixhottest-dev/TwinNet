import os
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import datetime
from openai import OpenAI

app = FastAPI(title="TwinNet Core Gateway")
security = HTTPBearer()

# Render se NVIDIA API Key fetch karna
raw_key = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_API_KEY = raw_key.strip()

if not NVIDIA_API_KEY:
    print("CRITICAL WARNING: NVIDIA_API_KEY is missing in Render!")

# NVIDIA ka endpoint aur key set karna
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

class TwinCommand(BaseModel):
    command: str

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return "user_999_verified"

@app.get("/")
async def health_check():
    return {"status": "TwinNet Backend is Live with NVIDIA AI!"}

@app.post("/v1/twin/interact")
async def interact_with_twin(
    request: TwinCommand, 
    user_id: str = Depends(verify_token)
):
    if not NVIDIA_API_KEY:
        raise HTTPException(status_code=500, detail="Render API Key Error: NVIDIA_API_KEY is missing.")

    try:
        prompt = f"Tu {user_id} ka ek highly intelligent 'Personal AI Twin' hai. User ne command diya hai: '{request.command}'. Smartly bata ki tu ye kaise execute karega."
        
        # ✅ THE FIX: NVIDIA ka sabse latest aur active Llama 3.1 model
        completion = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_reply = completion.choices[0].message.content
        
        return {
            "status": "success",
            "timestamp": str(datetime.datetime.now()),
            "ai_response": ai_reply
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NVIDIA Engine Error: {str(e)}")
