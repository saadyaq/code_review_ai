import ast
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional

from src.analyzer import analyze_code_quality
from src.llm_client import auto_fix_pipeline

app=FastAPI(title="Code Review AI")

class CodeAnalysisRequest(BaseModel):
    code:str
    auto_fix:bool=False

class CodeAnalysisResponse(BaseModel):
    issues:List[Dict]
    fixed_code: Optional[str]=None
    diff:Optional[str]=None

@app.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(request:CodeAnalysisRequest):
    """Python code analysis"""

    try :
        tree=ast.parse(request.code)
        issues=analyze_code_quality(tree, request.code)
        
        result={
            "issues":issues
        }
        
        if request.auto_fix:
            fixed=auto_fix_pipeline(request.code)
            result["fixed_code"]=fixed["fixed"]
            result["diff"]=fixed["diff"]
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/health')
async def health():
    """Health check."""
    return {"status" : "ok"}