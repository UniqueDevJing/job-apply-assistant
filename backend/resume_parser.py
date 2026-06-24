"""简历解析 - 支持 PDF 和 DOCX"""
import os


async def parse_resume(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    if ext == ".pdf":
        text = _parse_pdf(file_path)
    elif ext in (".docx", ".doc"):
        text = _parse_docx(file_path)
    elif ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        return {"error": f"不支持的文件格式: {ext}"}

    return _extract_info(text)


def _parse_pdf(file_path: str) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _parse_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_info(text: str) -> dict:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return {
        "name": lines[0] if lines else "",
        "raw": text,
        "skills": _find_section(text, ["技能", "技术栈", "专业技能"]),
        "experience": _find_section(text, ["工作经历", "工作经验", "实习经历"]),
        "education": _find_section(text, ["教育背景", "学历", "教育经历"]),
        "projects": _find_section(text, ["项目经历", "项目经验"]),
    }


def _find_section(text: str, keywords: list[str]) -> str:
    for kw in keywords:
        idx = text.find(kw)
        if idx >= 0:
            return text[idx:idx+500].strip()
    return ""
