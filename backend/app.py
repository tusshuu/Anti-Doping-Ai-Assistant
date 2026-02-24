from database.auth_db import SessionLocal, SearchHistory
from auth_routes import router as auth_router
from database.auth_db import init_db, get_user_by_email
from fastapi import UploadFile, File, Depends, HTTPException
import shutil
from modules.ocr_module import extract_text_from_image
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from compliance_engine import check_drugs
from modules.nlp_module import find_multiple_drugs
from modules.llm_handler import ask_llm
from modules.llm_handler import extract_medicines_from_prescription
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from auth_routes import get_current_user
import os

# =============================
# APP INIT
# =============================

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
app.include_router(auth_router)

# =============================
# JWT CONFIG (IMPORTANT)
# =============================

SECRET_KEY = "your_secret_key_here"  # must match auth_routes
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



# =============================
# AUTHENTICATED PROFILE ROUTE
# =============================

from fastapi import Depends
from auth_routes import get_current_user

@app.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {
        "name": current_user.name,
        "email": current_user.email,
        "gender": getattr(current_user, "gender", "Not Provided"),
        "sport": current_user.sport,
        "subscription": "Active"
    }

   

# =============================
# TEXT CHECK
# =============================

class CheckRequest(BaseModel):
    text: str


@app.post("/check")
def check(data: CheckRequest, current_user = Depends(get_current_user)):

    detected = find_multiple_drugs(data.text)
    results = check_drugs(detected)

    explanation = ask_llm(
        f"Explain in simple terms for an athlete why these medicines are safe or risky: {detected}"
    )

    # ✅ Save search in DB
    db = SessionLocal()
    history = SearchHistory(
        user_id=current_user.id,
        searched_text=data.text,
        result_summary=str(results)
    )
    db.add(history)
    db.commit()
    db.close()

    return {
        "results": results,
        "ai_explanation": explanation
    }

# =============================
# CHAT
# =============================

@app.post("/chat")
def chat_with_ai(query: str):
    response = ask_llm(query)
    return {"response": response}

# =============================
# IMAGE CHECK
# =============================

@app.post("/check-image")
async def check_image(file: UploadFile = File(...)):

    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_image(file_location)
    os.remove(file_location)

    medicines_raw = extract_medicines_from_prescription(extracted_text)
    detected = [m.strip() for m in medicines_raw.split(",") if m.strip()]

    if not detected:
        return {
            "extracted_text": extracted_text,
            "results": [],
            "message": "No recognizable medicine found."
        }

    results = check_drugs(detected)

    explanation = ask_llm(
        f"Explain in simple terms for an athlete why these medicines are safe or risky: {detected}"
    )

    return {
        "extracted_text": extracted_text,
        "detected_medicines": detected,
        "results": results,
        "ai_explanation": explanation
    }

# =============================
# HEALTH CHECK
# =============================

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/history")
def get_history(current_user = Depends(get_current_user)):

    db = SessionLocal()
    history = db.query(SearchHistory)\
        .filter(SearchHistory.user_id == current_user.id)\
        .order_by(SearchHistory.created_at.desc())\
        .all()
    db.close()

    return [
        {
            "text": h.searched_text,
            "result": h.result_summary,
            "date": h.created_at
        }
        for h in history
    ]