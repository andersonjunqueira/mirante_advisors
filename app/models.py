from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database import Base

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"
    id = Column(Integer, primary_key=True, index=True)
    code_snippet = Column(Text, nullable=False)
    suggestions = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))