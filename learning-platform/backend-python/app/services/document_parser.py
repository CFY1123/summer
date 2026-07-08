from pathlib import Path

from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class UnsupportedDocumentTypeError(ValueError):
    pass


def parse_document(file_path: str | Path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise UnsupportedDocumentTypeError(f"Unsupported document type: {suffix}. Supported types are: {supported}")

    if suffix == ".pdf":
        return _parse_pdf(path)
    if suffix == ".docx":
        return _parse_docx(path)
    return _parse_txt(path)


def _parse_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    page_texts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            page_texts.append(text.strip())
    return _clean_text("\n\n".join(page_texts))


def _parse_docx(path: Path) -> str:
    doc = Document(str(path))
    paragraphs = [paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip()]
    return _clean_text("\n\n".join(paragraphs))


def _parse_txt(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            return _clean_text(path.read_text(encoding=encoding))
        except UnicodeDecodeError:
            continue
    return _clean_text(path.read_text(encoding="utf-8", errors="ignore"))


def _clean_text(text: str) -> str:
    text = text.lstrip("\ufeff")
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    compact_lines = [line for line in lines if line]
    return "\n".join(compact_lines)
