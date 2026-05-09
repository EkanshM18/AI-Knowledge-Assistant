from typing import Any, TypedDict


class GeneralAgentState(TypedDict, total=False):
    session_id: str
    question: str
    route: str
    history: list[dict[str, str]]
    history_text: str
    tool_name: str
    tool_input: dict[str, Any]
    tool_results: list[dict[str, Any]]
    answer: str
    validation_notes: str
    grounded: bool

