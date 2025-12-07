import os
import json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import google.generativeai as genai

# --- Configuration ---
API_KEY_FILE = "placify_env/gemini_api.txt"

def load_api_key():
    """Loads the Gemini API key from the specified file."""
    try:
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: API key file not found at {API_KEY_FILE}")
        return None

GEMINI_API_KEY = load_api_key()

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    print("Warning: Gemini API Key not loaded. AI features will not work.")
    model = None

# --- Data Loading ---
COMPANIES_FILE = "companies.json"

def load_companies():
    """Loads company data from JSON file."""
    try:
        with open(COMPANIES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Companies file not found at {COMPANIES_FILE}")
        return []

companies_data = load_companies()

# --- FastAPI Setup ---
app = FastAPI()

# Mount static files (css, js, images)
# We mount the current directory to serve index.html and script.js directly for this prototype
app.mount("/static", StaticFiles(directory="."), name="static")

class AssessmentRequest(BaseModel):
    mode: str
    dsa_skill: str
    project_description: str

# --- Routes ---

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/script.js")
async def read_script():
    return FileResponse('script.js')

@app.post("/api/assess")
async def generate_assessment(request: AssessmentRequest):
    """
    Generates a personalized assessment report using Gemini and local data.
    
    API Testing Instructions:
    -------------------------
    You can test this endpoint using 'curl' or Postman.
    
    Using curl:
    curl -X POST "http://127.0.0.1:8000/api/assess" \
         -H "Content-Type: application/json" \
         -d '{"mode": "balanced", "dsa_skill": "Intermediate", "project_description": "Built a Python web scraper"}'
    
    Expected Response:
    A JSON object containing:
    - readiness_score (int)
    - strengths (list)
    - gaps (list)
    - action_plan (list)
    - job_recommendations (list)
    - email_draft (str)
    """
    
    if not model:
        return JSONResponse(content={"error": "Gemini API key not configured"}, status_code=500)

    # 1. Construct Prompt for Gemini
    prompt = f"""
    Act as a career counselor. Analyze the following student profile:
    - Assessment Mode: {request.mode}
    - DSA Proficiency: {request.dsa_skill}
    - Project: {request.project_description}

    Based on this, generate a JSON object with the following keys:
    - readiness_score: An integer between 0 and 100.
    - strengths: A list of 3 key technical strengths.
    - gaps: A list of 3 areas for improvement.
    - action_plan: A list of 3 actionable steps (e.g., "Practice Graphs on LeetCode").
    - email_draft: A professional email draft to a recruiter at a tech company expressing interest in a role.
    
    Return ONLY valid JSON. Do not include markdown formatting like ```json.
    """

    try:
        # 2. Call Gemini API
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Clean up potential markdown formatting if Gemini adds it despite instructions
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        ai_data = json.loads(text_response)

        # 3. Simple Job Matching Logic (Mock RAG)
        # In a real RAG system, we would embed the user profile and query a vector DB.
        # Here, we do a simple keyword match or just return a random subset for the prototype.
        
        # Simple match: if project mentions python, recommend python jobs.
        recommended_jobs = []
        user_context = (request.project_description + " " + request.dsa_skill).lower()
        
        for company in companies_data:
            score = 0
            for skill in company['skills']:
                if skill.lower() in user_context:
                    score += 1
            
            # Artificial boost for demonstration
            match_percentage = min(95, 70 + (score * 5)) 
            
            job_entry = {
                "role": company['role'],
                "company": company['name'],
                "location": company['location'],
                "match": f"{match_percentage}%"
            }
            recommended_jobs.append(job_entry)

        # Return combined data
        return {
            "readiness_score": ai_data.get("readiness_score", 75),
            "strengths": ai_data.get("strengths", []),
            "gaps": ai_data.get("gaps", []),
            "action_plan": ai_data.get("action_plan", []),
            "email_draft": ai_data.get("email_draft", "Error generating draft."),
            "job_recommendations": recommended_jobs[:3] # Return top 3
        }

    except Exception as e:
        print(f"Error calling Gemini or parsing response: {e}")
        return JSONResponse(content={"error": "Failed to generate assessment"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    # Use 127.0.0.1 to avoid issues with some windows setups defaulting to ipv6
    uvicorn.run(app, host="127.0.0.1", port=8000)
