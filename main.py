import os
import google.generativeai as genai
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import datetime

app = FastAPI(title="TwinNet Core Gateway")
security = HTTPBearer()

# Render se API Key fetch karna
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set!")

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
    try:
        # 1. AUTO-DETECT: Google se pucho ki is key ke liye kaunse models allowed hain
        target_model_name = None
        
        # Pehle sabse fast 'flash' model dhoondhne ki koshish
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name:
                    target_model_name = m.name
                    break
        
        # Agar flash nahi mila, toh jo bhi pehla available model ho use utha lo
        if not target_model_name:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    target_model_name = m.name
                    break
                    
        if not target_model_name:
            raise Exception("Is API key par koi bhi Text-Generation model available nahi hai.")

        # 'models/' prefix ko hata kar clean naam nikalna
        clean_name = target_model_name.replace("models/", "")
        
        # 2. Jo model exactly available hai, usko initialize karna
        model = genai.GenerativeModel(clean_name)
        
        prompt = f"Tu {user_id} ka ek highly intelligent 'Personal AI Twin' hai. User ne command diya hai: '{request.command}'. Smartly bata ki tu ye kaise execute karega."
        
        # 3. AI Reply Generate karna
        response = model.generate_content(prompt)
        
        return {
            "status": "success",
            "timestamp": str(datetime.datetime.now()),
            # UI par dikhane ke liye shuru mein model ka naam bhi bhej rahe hain
            "ai_response": f"[{clean_name}] {response.text}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-Detect Error: {str(e)}")
