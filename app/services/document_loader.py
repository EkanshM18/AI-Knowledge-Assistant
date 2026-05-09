import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from llama_index.core import Document
from pypdf import PdfReader


class DocumentLoader:
    supported_extensions = {".pdf", ".txt", ".docx", ".md", ".csv", ".json", ".html", ".htm"}

    def load(self, file_path: Path, tags: list[str] | None = None) -> list[Document]:
        suffix = file_path.suffix.lower()
        if suffix not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {suffix}")

        tags = tags or []
        timestamp = datetime.now(timezone.utc).isoformat()

        if suffix == ".pdf":
            return self._load_pdf(file_path, tags, timestamp)
        if suffix == ".docx":
            text = self._load_docx_text(file_path)
        elif suffix in {".html", ".htm"}:
            text = self._load_html_text(file_path)
        elif suffix == ".csv":
            text = self._load_csv_text(file_path)
        elif suffix == ".json":
            text = self._load_json_text(file_path)
        else:
            text = file_path.read_text(encoding="utf-8", errors="ignore")

        return [self._build_document(file_path, text, tags, timestamp)]

    def _load_pdf(self, file_path: Path, tags: list[str], timestamp: str) -> list[Document]:
        documents: list[Document] = []
        reader = PdfReader(str(file_path))
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            documents.append(self._build_document(file_path, text, tags, timestamp, page_number=page_number))
        return documents

    def _load_docx_text(self, file_path: Path) -> str:
        document = DocxDocument(str(file_path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())

    def _load_html_text(self, file_path: Path) -> str:
        html = file_path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text(separator="\n", strip=True)

    def _load_csv_text(self, file_path: Path) -> str:
        rows: list[str] = []
        with file_path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                rows.append(" | ".join(cell.strip() for cell in row))
        return "\n".join(rows)

    def _load_json_text(self, file_path: Path) -> str:
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            payload = json.load(handle)
        return json.dumps(payload, indent=2, ensure_ascii=True)

    def _build_document(
        self,
        file_path: Path,
        text: str,
        tags: list[str],
        timestamp: str,
        page_number: int | None = None,
    ) -> Document:
        metadata = {
            "filename": file_path.name,
            "page_number": page_number,
            "source": str(file_path),
            "tags": tags,
            "timestamp": timestamp,
        }
        doc_id = f"{file_path.name}:{page_number or 0}"
        return Document(text=text, metadata=metadata, doc_id=doc_id)

