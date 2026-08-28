from typing import List
from pydantic import BaseModel


class KnowledgeBaseReference(BaseModel):
    source: str
    relevance: float


class TriageResult(BaseModel):
    product_area: str
    issue_category: str
    urgency: str
    reasoning: str
    known_issue: bool
    knowledge_base_references: List[KnowledgeBaseReference]
    recommended_team: str
    first_response: str