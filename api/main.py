from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

from src.analyzer import analyze_code_quality
from src.llm_client import auto_fix_pipeline

app = FastAPI(title="Code Review AI", redirect_slashes=False)

# Import webhook routes (must be after app creation)
from api import webhook  # noqa: F401

class CodeAnalysisRequest(BaseModel):
    code: str
    auto_fix: bool = False

class CodeAnalysisResponse(BaseModel):
    issues: List[Dict]
    fixed_code: Optional[str] = None
    diff: Optional[str] = None

@app.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """Python code analysis"""

    try:
        # Analyze code quality
        analysis_result = analyze_code_quality(code=request.code)

        result = {
            "issues": analysis_result['issues']
        }

        if request.auto_fix:
            fixed = auto_fix_pipeline(code=request.code)
            result["fixed_code"] = fixed["fixed"]
            result["diff"] = fixed["diff"]

        return result

    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Python syntax: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get('/health')
async def health():
    """Health check."""
    return {"status" : "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)