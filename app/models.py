from pydantic import BaseModel
from typing import Dict, Any, Optional

class AssessmentSubmission(BaseModel):
    mode: str
    answers: Dict[str, Any]
    resume_filename: Optional[str] = None # Optional resume linkage
