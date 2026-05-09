from __future__ import annotations

import re

from transformers import pipeline

from app.core.config import Settings
from app.prompts.system_prompts import (
    build_enterprise_memory_prompt,
    build_enterprise_retrieval_prompt,
    build_general_assistant_prompt,
    enterprise_redirect_to_general_bot,
)


class GenerationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._pipeline = None
        self._task = self._resolve_task(settings.llm_model)

    def _resolve_task(self, model_name: str) -> str:
        if "flan" in model_name.lower() or "t5" in model_name.lower():
            return "text2text-generation"
        return "text-generation"

    def _get_pipeline(self):
        if self._pipeline is None:
            device = -1 if self.settings.llm_device == "cpu" else 0
            self._pipeline = pipeline(
                task=self._task,
                model=self.settings.llm_model,
                device=device,
            )
        return self._pipeline

    def _run_generation(self, prompt: str) -> str:
        generator = self._get_pipeline()
        outputs = generator(
            prompt,
            max_new_tokens=self.settings.llm_max_new_tokens,
            do_sample=self.settings.llm_temperature > 0.2,
            temperature=self.settings.llm_temperature,
        )
        text = outputs[0]["generated_text"].strip()
        if self._task == "text-generation" and text.startswith(prompt):
            text = text[len(prompt) :].strip()
        return self._clean_generated_text(text)

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: list[dict],
        history_text: str,
        route: str,
    ) -> str:
        if route == "general_redirect":
            return enterprise_redirect_to_general_bot()

        if route != "memory" and not retrieved_chunks:
            return (
                "I do not have enough context in the uploaded enterprise knowledge to answer that yet. "
                "Please upload relevant documents or refine the question."
            )

        context_lines = []
        for index, chunk in enumerate(retrieved_chunks, start=1):
            label = f"[S{index}] {chunk['filename']}"
            if chunk.get("page_number"):
                label += f" page {chunk['page_number']}"
            context_lines.append(f"{label}\n{chunk['text']}")

        context = "\n\n".join(context_lines)[: self.settings.max_context_characters]
        prompt = self._build_prompt(question, history_text, context, route)
        return self._run_generation(prompt)

    def generate_general_response(
        self,
        question: str,
        route: str,
        history_text: str,
        tool_results: list[dict],
    ) -> str:
        if route != "conversation" and tool_results:
            summaries = [item.get("summary", "").strip() for item in tool_results if item.get("summary")]
            return "\n".join(summary for summary in summaries if summary).strip()

        prompt = build_general_assistant_prompt(history_text=history_text, question=question)
        return self._run_generation(prompt)

    def _clean_generated_text(self, text: str) -> str:
        cleaned = text.strip()
        cleaned = re.sub(r"^(answer|response)\s*:\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^(assistant|user|system)\s*:\s*", "", cleaned, flags=re.IGNORECASE)

        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        if lines:
            first_line = re.sub(r"^(assistant|user|system)\s*:\s*", "", lines[0], flags=re.IGNORECASE)
            lines[0] = first_line.strip()
            cleaned = "\n".join(lines)

        return cleaned.strip()

    def _build_prompt(self, question: str, history_text: str, context: str, route: str) -> str:
        if route == "memory":
            return build_enterprise_memory_prompt(history_text=history_text, question=question)

        return build_enterprise_retrieval_prompt(
            history_text=history_text,
            context=context,
            question=question,
        )

