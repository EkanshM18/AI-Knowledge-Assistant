from typing import Any, TypedDict


class EnterpriseAgentState(TypedDict, total=False):
    session_id: str
    question: str
    route: str
    top_k: int
    metadata_filters: dict[str, Any]
    history: list[dict[str, str]]
    history_text: str
    retrieved_chunks: list[dict[str, Any]]
    answer: str
    grounded: bool
    validation_notes: str

