from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import datetime

app = FastAPI(title="TwinNet Core Gateway")
security = HTTPBearer()

# Pydantic Schema: Notice we DO NOT ask for user_id or tokens in the body
class TwinCommand(BaseModel):
    command: str

# Mock JWT Decoder (In production, use python-jose to decode real JWTs)
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Dummy verification: In reality, decode token and query PostgreSQL
    if token == "invalid_token":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Extract user_id from the decoded JWT payload
    extracted_user_id = "user_999_verified" 
    return extracted_user_id

@app.post("/v1/twin/interact")
async def interact_with_twin(
    request: TwinCommand, 
    user_id: str = Depends(verify_token)  # Identity is established securely here
):
    # 1. Log the secure request
    print(f"[SECURE] Processing command for {user_id}: {request.command}")
    
    # 2. Synchronous Gemini Loop (For Milestone 1 verification)
    # prompt = f"Context: You are the twin of {user_id}. User command: {request.command}"
    # gemini_response = gemini_model.generate_content(prompt)
    mock_gemini_response = f"I am ready to execute: '{request.command}' on behalf of {user_id}"

    # 3. Return to Sketchware
    return {
        "status": "success",
        "timestamp": str(datetime.datetime.now()),
        "ai_response": mock_gemini_response
    }
  
