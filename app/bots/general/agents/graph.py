from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.bots.general.agents.state import GeneralAgentState
from app.bots.general.services.tool_service import GeneralToolService
from app.services.generation_service import GenerationService
from app.services.memory_service import MemoryService


class GeneralAssistantGraph:
    def __init__(
        self,
        memory_service: MemoryService,
        tool_service: GeneralToolService,
        generation_service: GenerationService,
    ) -> None:
        self.memory_service = memory_service
        self.tool_service = tool_service
        self.generation_service = generation_service
        self.graph = self._build()

    def _build(self):
        builder = StateGraph(GeneralAgentState)
        builder.add_node("memory", self._memory_node)
        builder.add_node("router", self._router_node)
        builder.add_node("tool_executor", self._tool_executor_node)
        builder.add_node("synthesizer", self._synthesizer_node)
        builder.add_node("validator", self._validator_node)

        builder.add_edge(START, "memory")
        builder.add_edge("memory", "router")
        builder.add_conditional_edges("router", self._route_edge)
        builder.add_edge("tool_executor", "synthesizer")
        builder.add_edge("synthesizer", "validator")
        builder.add_edge("validator", END)
        return builder.compile()

    def invoke(self, state: GeneralAgentState) -> GeneralAgentState:
        return self.graph.invoke(state)

    def _memory_node(self, state: GeneralAgentState) -> GeneralAgentState:
        session_id = state["session_id"]
        history = self.memory_service.get_history(session_id, limit=10)
        history_text = self.memory_service.render_history(session_id, limit=10)
        return {"history": history, "history_text": history_text}

    def _router_node(self, state: GeneralAgentState) -> GeneralAgentState:
        route, tool_input = self.tool_service.detect_intent(state["question"])
        return {
            "route": route,
            "tool_name": route if route != "conversation" else "",
            "tool_input": tool_input,
        }

    def _route_edge(self, state: GeneralAgentState) -> Literal["tool_executor", "synthesizer"]:
        return "synthesizer" if state.get("route") == "conversation" else "tool_executor"

    def _tool_executor_node(self, state: GeneralAgentState) -> GeneralAgentState:
        result = self.tool_service.execute(state.get("tool_name", ""), state.get("tool_input", {}))
        return {"tool_results": [result]}

    def _synthesizer_node(self, state: GeneralAgentState) -> GeneralAgentState:
        answer = self.generation_service.generate_general_response(
            question=state["question"],
            route=state.get("route", "conversation"),
            history_text=state.get("history_text", ""),
            tool_results=state.get("tool_results", []),
        )
        return {"answer": answer}

    def _validator_node(self, state: GeneralAgentState) -> GeneralAgentState:
        tool_results = state.get("tool_results", [])
        if not tool_results:
            return {
                "grounded": True,
                "validation_notes": "General conversation response generated without external tools.",
            }

        statuses = {result.get("status") for result in tool_results}
        grounded = "success" in statuses and "error" not in statuses
        note = (
            "Answer synthesized from tool outputs."
            if grounded
            else "One or more tools could not complete, so the answer may be partial."
        )
        return {"grounded": grounded, "validation_notes": note}

