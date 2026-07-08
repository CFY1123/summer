import re


def split_text(text: str, chunk_size: int = 800) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n+", text) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 1 <= chunk_size:
            current = f"{current}\n{paragraph}".strip()
            continue
        if current:
            chunks.append(current)
        current = paragraph

    if current:
        chunks.append(current)
    return chunks or ([text.strip()] if text.strip() else [])


def summarize_text(text: str, max_length: int = 280) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[:max_length].rstrip() + "..."


def pick_keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[\u4e00-\u9fa5]{2,}|[A-Za-z][A-Za-z0-9_-]{2,}", text)
    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "课程",
        "学习",
        "内容",
        "知识",
        "系统",
    }
    counts: dict[str, int] = {}
    for word in words:
        key = word.lower()
        if key in stop_words:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked[:limit]]


def make_question_from_text(text: str, index: int, difficulty: str = "medium") -> dict:
    keywords = pick_keywords(text, limit=4)
    answer = keywords[0] if keywords else "核心概念"
    distractors = (keywords[1:] + ["学习目标", "章节结构", "练习方法"])[:3]
    options = [answer, *distractors]
    while len(options) < 4:
        options.append(f"选项{len(options) + 1}")

    return {
        "questionType": "single_choice",
        "difficulty": difficulty,
        "stem": f"根据本章节资料，以下哪一项最能代表知识点 {index}？",
        "options": options[:4],
        "answer": answer,
        "analysis": summarize_text(text, 160) or "该题根据章节资料自动生成。",
    }
