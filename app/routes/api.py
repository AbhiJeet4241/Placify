import os
import json
import time
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from app.config import RESUME_DIR, PDF_DIR
from app.models import AssessmentSubmission
from app.quiz import QUESTIONS_DB, companies_data
from app.services.resume_service import extract_resume_text
from app.services.matching_service import rank_companies
from app.services.ai_service import analyze_profile
from app.services.pdf_service import generate_pdf

router = APIRouter(prefix="/api")

@router.get("/report/pdf")
async def get_report(filename: str):
    file_path = os.path.join(PDF_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"error": "File not found"})

@router.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(RESUME_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        return {"info": f"file '{file.filename}' saved at '{file_location}'", "filename": file.filename}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/questions/{mode}")
async def get_questions(mode: str):
    if mode not in QUESTIONS_DB:
        raise HTTPException(status_code=404, detail="Invalid mode")
    return QUESTIONS_DB[mode]

@router.post("/assess")
async def generate_assessment(submission: AssessmentSubmission):
    # 1. Format User Context
    mode = submission.mode
    answers = submission.answers
    
    questions_list = QUESTIONS_DB.get(mode, [])
    user_context = f"Assessment Mode: {mode}\n"
    
    for q in questions_list:
        key = f"q_{q['id']}"
        ans = answers.get(key, "Not Answered")
        user_context += f"Q: {q['text']}\nA: {ans}\n"

    # 1.5 Extract Resume
    resume_text = ""
    if submission.resume_filename:
        resume_text = extract_resume_text(submission.resume_filename)
        user_context += f"\n--- RESUME CONTENT ---\n{resume_text[:2000]}..."

    # 2. Rank Companies
    top_candidates = rank_companies(user_context, companies_data)
    candidates_json = json.dumps([{
        "id": c['id'], "name": c['name'], "role": c['role'], 
        "skills": c['skills'], "email": c['email']
    } for c in top_candidates])

    # 3. Call AI
    ai_data = analyze_profile(user_context, candidates_json, mode, answers, bool(resume_text))
    top_jobs = ai_data.get("job_recommendations", [])

    # 4. Generate PDF
    report_filename = f"Placement_Report_{int(time.time())}.pdf"
    final_data = {
        "mode": submission.mode,
        **ai_data,
        "job_recommendations": top_jobs
    }
    
    try:
        generate_pdf(final_data, filename=report_filename)
    except Exception as e:
        print(f"PDF Error: {e}")

    final_data["pdf_url"] = f"/api/report/pdf?filename={report_filename}"
    return final_data
