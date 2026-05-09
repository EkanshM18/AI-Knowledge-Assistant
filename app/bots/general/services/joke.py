from __future__ import annotations

from random import choice


class JokeService:
    def __init__(self) -> None:
        self._jokes = [
            "Why did the AI bring a notebook to work? Because it wanted better memory retention.",
            "I told the chatbot to stay grounded. It replied, 'Only if you give me better sources.'",
            "Why did the data engineer stay calm? Because every pipeline issue was just a stream of opportunities.",
            "The vector database said it felt close to me. I guess our embeddings aligned.",
            "Why did the agent graph ace the interview? It always knew the next node to visit.",
        ]

    def tell(self) -> dict:
        return {
            "tool_name": "joke",
            "status": "success",
            "summary": choice(self._jokes),
            "source_label": "Local joke library",
            "source_url": "",
        }
