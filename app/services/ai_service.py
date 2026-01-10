import json
import os
import time
from google import genai
from app.config import GEMINI_API_KEY, ANALYSIS_DIR

client = None
model = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
    model = 'gemini-2.5-flash'
else:
    print("Warning: Gemini API Key not loaded. AI features will not work.")

def analyze_profile(user_context, candidates_json, mode, answers, resume_extracted):
    if not client:
        # Mock Data
        print("Using Mock Data (No API Key)")
        return {
            "readiness_score": 75,
            "strengths": ["Mock Strength 1", "Mock Strength 2"],
            "gaps": ["Mock Gap 1", "Mock Gap 2"],
            "action_plan": ["Mock Action 1", "Mock Action 2"],
            "email_draft": "Mock Email Draft",
            "candidate_name": "Mock Student",
            "job_recommendations": []
        }

    prompt = f"""
    Act as a career counselor. Analyze the following student profile and the provided list of matched companies.
    
    STUDENT PROFILE:
    {user_context}
    
    MATCHED COMPANIES (Select top 3 from this list ONLY):
    {candidates_json}
    
    Generate a JSON object with:
    - candidate_name: String (Extract full name from resume, or return "Dear Student" if unknown)
    - readiness_score: Integer (0-100)
    - strengths: List of 3 strings (Student's strengths)
    - gaps: List of 3 strings (Missing skills for these roles)
    - action_plan: List of 3 actionable steps
    - job_recommendations: List of 3 Objects from the "MATCHED COMPANIES" list provided above. Do NOT hallucinate companies.
      For each object include:
      - company: Name (Must exist in MATCHED COMPANIES)
      - role: Role
      - location: Location
      - match: Match Reason (Short string)
      - email_draft: A specific cold email draft to this company's HR. 
        The email must be professional, mention the specific role, and highlight the student's relevant strengths.
    
    - email_draft: (Legacy field, keep generic) "Generic inquiry..."
    
    Return ONLY valid JSON.
    """

    try:
        print("Sending prompt to Gemini...")
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        print("Received response.")
        
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        if text_response.startswith('json'):
            text_response = text_response[4:].strip()
        
        ai_data = json.loads(text_response)
        
        # Save Analysis
        timestamp = int(time.time())
        analysis_filename = f"analysis_{timestamp}.json"
        analysis_path = os.path.join(ANALYSIS_DIR, analysis_filename)
        
        with open(analysis_path, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "mode": mode,
                "submission": answers,
                "resume_extracted": resume_extracted,
                "candidates_provided": json.loads(candidates_json),
                "gemini_response": ai_data
            }, f, indent=4)
        print(f"Analysis saved to {analysis_path}")
        
        return ai_data

    except Exception as e:
        print(f"Gemini Error: {e}")
        return {
            "candidate_name": "Student",
            "readiness_score": 0,
            "strengths": [],
            "gaps": [],
            "action_plan": [],
            "email_draft": "Error generating report.",
            "job_recommendations": []
        }
