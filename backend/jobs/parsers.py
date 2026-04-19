"""
File parsers: extract raw text from PDF or DOCX.
"""
import fitz  # PyMuPDF
import docx


def parse_pdf(file) -> str:
    """Extract text from an in-memory PDF file object."""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def parse_docx(file) -> str:
    """Extract text from an in-memory DOCX file object."""
    document = docx.Document(file)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def extract_text(file, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return parse_pdf(file)
    elif ext in ("docx", "doc"):
        return parse_docx(file)
    raise ValueError(f"Unsupported file type: .{ext}")
