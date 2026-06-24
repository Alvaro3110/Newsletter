from typing import TypedDict, List, Dict, Any

class NewsletterState(TypedDict):
    """
    State definition for the Newsletter Cognitive State Machine (LangGraph).
    This structure is serialized and stored in SQLite checkpoints.
    """
    topic_context: str
    research_sources: List[Dict[str, Any]]  # Each dict: {"url": str, "snippet": str, "authority_score": float}
    analytical_points: List[Dict[str, str]]  # Each dict: {"pros": str, "cons": str, "decision_technical": str}
    essay_draft: str
    validation_logs: List[str]
    metadata: Dict[str, Any]
