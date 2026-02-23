from fastapi import UploadFile, File
import shutil
from modules.ocr_module import extract_text_from_image
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from compliance_engine import check_drugs
from modules.nlp_module import find_multiple_drugs
from compliance_engine import check_drugs
from modules.llm_handler import ask_llm

app = FastAPI()

# ✅ Enable CORS (VERY IMPORTANT for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request model
class CheckRequest(BaseModel):
    text: str


@app.post("/check")
def check(data: CheckRequest):

    # Step 1: Extract drug names
    detected = find_multiple_drugs(data.text)

    if not detected:
        explanation = ask_llm(
            f"No medicine detected in this text: {data.text}. Explain politely."
        )
        return {
            "results": [],
            "ai_explanation": explanation,
            "message": "No recognizable medicine found."
        }

    # Step 2: Check compliance
    results = check_drugs(detected)

    # Step 3: AI explanation
    explanation = ask_llm(
        f"Explain in simple terms for an athlete why these medicines are safe or risky: {detected}"
    )

    return {
        "results": results,
        "ai_explanation": explanation
    }


@app.post("/chat")
def chat_with_ai(query: str):
    response = ask_llm(query)
    return {"response": response}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/check-image")
async def check_image(file: UploadFile = File(...)):
    
    file_location = f"temp_{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    extracted_text = extract_text_from_image(file_location)

    # Convert extracted text into list of words
    drug_list = extracted_text.split()

    results = check_drugs(drug_list)

    return {
        "extracted_text": extracted_text,
        "results": results
    }