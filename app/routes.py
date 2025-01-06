from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import AnalysisHistory
from app.database import SessionLocal
from app.services import analyze_code

class CodeSnippet(BaseModel):
    code_snippet: str

router = APIRouter()
    
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze-code")
def analyze_code_endpoint(payload: CodeSnippet, db: Session = Depends(get_db)):
    # Gera sugestões como uma lista
    suggestions = analyze_code(payload.code_snippet)

    # Salva a análise no banco de dados
    analysis = AnalysisHistory(
        code_snippet=payload.code_snippet, 
        suggestions="\n".join(suggestions)  # Armazena como string no banco
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Retorna as sugestões como uma lista
    return {"id": analysis.id, "suggestions": suggestions}

@router.get("/health")
def health():
    return {"status": "ok"}
