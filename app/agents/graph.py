from __future__ import annotations

import re
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.state import AgentState
from app.services.generation_service import GenerationService
from app.services.memory_service import MemoryService
from app.services.retrieval_service import RetrievalService


class KnowledgeAssistantGraph:
    def __init__(
        self,
        memory_service: MemoryService,
        retrieval_service: RetrievalService,
        generation_service: GenerationService,
    ) -> None:
        self.memory_service = memory_service
        self.retrieval_service = retrieval_service
        self.generation_service = generation_service
        self.graph = self._build()

    def _build(self):
        builder = StateGraph(AgentState)
        builder.add_node("memory", self._memory_node)
        builder.add_node("router", self._router_node)
        builder.add_node("retriever", self._retriever_node)
        builder.add_node("synthesizer", self._synthesizer_node)
        builder.add_node("validator", self._validator_node)

        builder.add_edge(START, "memory")
        builder.add_edge("memory", "router")
        builder.add_conditional_edges("router", self._route_edge)
        builder.add_edge("retriever", "synthesizer")
        builder.add_edge("synthesizer", "validator")
        builder.add_edge("validator", END)
        return builder.compile()

    def invoke(self, state: AgentState) -> AgentState:
        return self.graph.invoke(state)

    def _memory_node(self, state: AgentState) -> AgentState:
        session_id = state["session_id"]
        history = self.memory_service.get_history(session_id, limit=8)
        history_text = self.memory_service.render_history(session_id, limit=8)
        return {"history": history, "history_text": history_text}

    def _router_node(self, state: AgentState) -> AgentState:
        question = state["question"].strip().lower()
        memory_only_markers = [
            "what did i ask",
            "what did we discuss",
            "previous message",
            "earlier question",
            "last response",
        ]
        summary_markers = ["summarize", "summary", "high level overview"]

        if any(marker in question for marker in memory_only_markers):
            route = "memory"
        elif any(marker in question for marker in summary_markers):
            route = "summarization"
        else:
            route = "retrieval"

        return {"route": route}

    def _route_edge(self, state: AgentState) -> Literal["retriever", "synthesizer"]:
        if state.get("route") == "memory":
            return "synthesizer"
        return "retriever"

    def _retriever_node(self, state: AgentState) -> AgentState:
        retrieved = self.retrieval_service.retrieve(
            query=state["question"],
            limit=state.get("top_k"),
            metadata_filters=state.get("metadata_filters"),
        )
        return {"retrieved_chunks": retrieved}

    def _synthesizer_node(self, state: AgentState) -> AgentState:
        answer = self.generation_service.generate_answer(
            question=state["question"],
            retrieved_chunks=state.get("retrieved_chunks", []),
            history_text=state.get("history_text", ""),
            route=state.get("route", "retrieval"),
        )
        return {"answer": answer}

    def _validator_node(self, state: AgentState) -> AgentState:
        answer = state.get("answer", "")
        chunks = state.get("retrieved_chunks", [])

        if not chunks:
            grounded = state.get("route") == "memory" or "do not have enough context" in answer.lower()
            note = "No retrieved context required." if grounded else "No supporting chunks were found."
            return {"grounded": grounded, "validation_notes": note}

        source_text = " ".join(chunk["text"] for chunk in chunks).lower()
        answer_terms = {
            token
            for token in re.findall(r"[a-z0-9]+", answer.lower())
            if len(token) > 3
        }
        overlap = sum(1 for token in answer_terms if token in source_text)
        grounded = overlap >= max(3, len(answer_terms) // 10)
        note = "Answer is sufficiently grounded in retrieved content." if grounded else (
            "Answer was softened because grounding confidence is low."
        )

        if not grounded:
            answer = (
                "I could not fully ground a confident answer in the retrieved enterprise knowledge. "
                "Please refine the question or upload more relevant documents."
            )

        return {
            "answer": answer,
            "grounded": grounded,
            "validation_notes": note,
        }

