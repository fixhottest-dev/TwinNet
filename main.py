import os
import google.generativeai as genai
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import datetime

app = FastAPI(title="TwinNet Core Gateway")
security = HTTPBearer()

# Render se API Key fetch karna aur extra spaces hatana
raw_key = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_KEY = raw_key.strip()

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("CRITICAL WARNING: GEMINI_API_KEY is missing in Render!")

class TwinCommand(BaseModel):
    command: str

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return "user_999_verified"

@app.get("/")
async def health_check():
    return {"status": "TwinNet Backend is Live!"}

@app.post("/v1/twin/interact")
async def interact_with_twin(
    request: TwinCommand, 
    user_id: str = Depends(verify_token)
):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Render API Key Error: GEMINI_API_KEY is missing.")

    try:
        # 🚀 THE FIX: Exact model version jo Google ne error mein manga hai
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        prompt = f"Tu {user_id} ka ek highly intelligent 'Personal AI Twin' hai. User ne command diya hai: '{request.command}'. Smartly bata ki tu ye kaise execute karega."
        
        # Real Gemini API Call
        response = model.generate_content(prompt)
        
        return {
            "status": "success",
            "timestamp": str(datetime.datetime.now()),
            "ai_response": response.text
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")
