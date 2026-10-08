import os
import google.generativeai as genai
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import datetime

app = FastAPI(title="TwinNet Core Gateway")
security = HTTPBearer()

# Render se API Key automatically fetch karna
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set in Environment Variables!")

# ✅ ERROR FIX: Model ka naam 'gemini-1.5-flash-latest' kar diya gaya hai
model = genai.GenerativeModel('gemini-1.5-flash-latest')

class TwinCommand(BaseModel):
    command: str

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token == "invalid_token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return "user_999_verified"

# ✅ NEW: Server check karne ke liye base route
@app.get("/")
async def health_check():
    return {"status": "TwinNet Backend is Live and Ready!"}

@app.post("/v1/twin/interact")
async def interact_with_twin(
    request: TwinCommand, 
    user_id: str = Depends(verify_token)
):
    try:
        # 1. Twin ke liye Prompt design karna
        prompt = f"Tu {user_id} ka ek highly intelligent 'Personal AI Twin' hai. User ne tujhe ye command diya hai: '{request.command}'. Ek smart aur concise reply de ki tu ye kaise execute karega."
        
        # 2. Real Gemini API Call
        response = model.generate_content(prompt)
        ai_reply = response.text

        # 3. Sketchware ko wapas response bhejna
        return {
            "status": "success",
            "timestamp": str(datetime.datetime.now()),
            "ai_response": ai_reply
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")
