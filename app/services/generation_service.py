from __future__ import annotations

from transformers import pipeline

from app.core.config import Settings


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

    def generate_answer(
        self,
        question: str,
        retrieved_chunks: list[dict],
        history_text: str,
        route: str,
    ) -> str:
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
        return text

    def _build_prompt(self, question: str, history_text: str, context: str, route: str) -> str:
        if route == "memory":
            return (
                "You are an enterprise assistant.\n"
                "Answer only from the conversation history below.\n"
                "If the history does not contain the answer, say you do not know.\n\n"
                f"Conversation history:\n{history_text or 'No previous conversation.'}\n\n"
                f"User question: {question}\n\n"
                "Answer:"
            )

        return (
            "You are an enterprise AI knowledge assistant.\n"
            "Answer only from the retrieved context.\n"
            "Do not invent facts. If the answer is not in the context, say so clearly.\n"
            "When you use evidence, cite sources like [S1], [S2].\n\n"
            f"Conversation history:\n{history_text or 'No previous conversation.'}\n\n"
            f"Retrieved context:\n{context or 'No context available.'}\n\n"
            f"User question: {question}\n\n"
            "Grounded answer:"
        )

