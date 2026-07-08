import json
import re
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import ROOT_DIR, settings
from app.services.db_utils import camel_row
from app.services.document_parser import SUPPORTED_EXTENSIONS, parse_document
from app.services.text_utils import make_question_from_text, pick_keywords, split_text, summarize_text


DEFAULT_USER_ID = 1


def ensure_default_user(db: Session) -> None:
    db.execute(
        text(
            """
            INSERT INTO users (id, username, password_hash, display_name)
            VALUES (1, 'admin', 'change-me-later', 'Admin')
            ON DUPLICATE KEY UPDATE display_name = VALUES(display_name)
            """
        )
    )
    db.commit()


def create_knowledge_base(db: Session, name: str, description: str | None = None) -> dict:
    collection = f"kb_{uuid4().hex[:16]}"
    result = db.execute(
        text(
            """
            INSERT INTO knowledge_bases (name, description, vector_collection)
            VALUES (:name, :description, :collection)
            """
        ),
        {"name": name, "description": description, "collection": collection},
    )
    db.commit()
    return get_knowledge_base(db, int(result.lastrowid))


def list_knowledge_bases(db: Session) -> list[dict]:
    rows = db.execute(
        text(
            """
            SELECT id, name, description, vector_collection, document_count, chunk_count,
                   create_time, update_time
            FROM knowledge_bases
            ORDER BY update_time DESC, id DESC
            """
        )
    )
    return [camel_row(row) for row in rows]


def get_knowledge_base(db: Session, kb_id: int) -> dict:
    row = db.execute(
        text(
            """
            SELECT id, name, description, vector_collection, document_count, chunk_count,
                   create_time, update_time
            FROM knowledge_bases
            WHERE id = :id
            """
        ),
        {"id": kb_id},
    ).first()
    if row is None:
        raise ValueError("Knowledge base not found.")
    return camel_row(row)


def delete_knowledge_base(db: Session, kb_id: int) -> None:
    get_knowledge_base(db, kb_id)
    db.execute(text("DELETE FROM wrong_questions WHERE question_id IN (SELECT id FROM questions WHERE chapter_id IN (SELECT id FROM course_chapters WHERE knowledge_base_id = :id))"), {"id": kb_id})
    db.execute(text("DELETE FROM quiz_answers WHERE question_id IN (SELECT id FROM questions WHERE chapter_id IN (SELECT id FROM course_chapters WHERE knowledge_base_id = :id))"), {"id": kb_id})
    db.execute(text("DELETE FROM quiz_attempts WHERE chapter_id IN (SELECT id FROM course_chapters WHERE knowledge_base_id = :id)"), {"id": kb_id})
    db.execute(text("DELETE FROM questions WHERE chapter_id IN (SELECT id FROM course_chapters WHERE knowledge_base_id = :id)"), {"id": kb_id})
    db.execute(text("DELETE FROM chapter_progress WHERE chapter_id IN (SELECT id FROM course_chapters WHERE knowledge_base_id = :id)"), {"id": kb_id})
    db.execute(text("DELETE FROM course_chapters WHERE knowledge_base_id = :id"), {"id": kb_id})
    db.execute(text("DELETE FROM document_chunks WHERE knowledge_base_id = :id"), {"id": kb_id})
    db.execute(text("DELETE FROM documents WHERE knowledge_base_id = :id"), {"id": kb_id})
    db.execute(text("DELETE FROM knowledge_bases WHERE id = :id"), {"id": kb_id})
    db.commit()


def list_documents(db: Session, kb_id: int) -> list[dict]:
    get_knowledge_base(db, kb_id)
    rows = db.execute(
        text(
            """
            SELECT id, knowledge_base_id, filename, file_type, file_path, parser_status,
                   chunk_count, error_message, create_time, update_time
            FROM documents
            WHERE knowledge_base_id = :kb_id
            ORDER BY create_time DESC, id DESC
            """
        ),
        {"kb_id": kb_id},
    )
    return [camel_row(row) for row in rows]


def save_uploaded_document(db: Session, kb_id: int, file: UploadFile) -> dict:
    get_knowledge_base(db, kb_id)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Only {supported} files are supported.")

    upload_dir = ROOT_DIR / settings.upload_dir / str(kb_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}{suffix}"
    stored_path = upload_dir / safe_name
    with stored_path.open("wb") as target:
        shutil.copyfileobj(file.file, target)

    result = db.execute(
        text(
            """
            INSERT INTO documents (knowledge_base_id, filename, file_type, file_path, parser_status)
            VALUES (:kb_id, :filename, :file_type, :file_path, 'pending')
            """
        ),
        {
            "kb_id": kb_id,
            "filename": file.filename or safe_name,
            "file_type": suffix.lstrip("."),
            "file_path": str(stored_path),
        },
    )
    document_id = int(result.lastrowid)

    try:
        parsed_text = parse_document(stored_path)
        chunks = split_text(parsed_text)
        for index, chunk in enumerate(chunks):
            db.execute(
                text(
                    """
                    INSERT INTO document_chunks (document_id, knowledge_base_id, chunk_index, content)
                    VALUES (:document_id, :kb_id, :chunk_index, :content)
                    """
                ),
                {"document_id": document_id, "kb_id": kb_id, "chunk_index": index, "content": chunk},
            )
        db.execute(
            text(
                """
                UPDATE documents
                SET parser_status = 'success', chunk_count = :chunk_count, error_message = NULL
                WHERE id = :id
                """
            ),
            {"chunk_count": len(chunks), "id": document_id},
        )
    except Exception as exc:
        db.execute(
            text(
                """
                UPDATE documents
                SET parser_status = 'failed', error_message = :message
                WHERE id = :id
                """
            ),
            {"message": str(exc)[:1000], "id": document_id},
        )

    refresh_knowledge_base_counts(db, kb_id)
    db.commit()
    return get_document(db, document_id)


def get_document(db: Session, document_id: int) -> dict:
    row = db.execute(
        text(
            """
            SELECT id, knowledge_base_id, filename, file_type, file_path, parser_status,
                   chunk_count, error_message, create_time, update_time
            FROM documents
            WHERE id = :id
            """
        ),
        {"id": document_id},
    ).first()
    if row is None:
        raise ValueError("Document not found.")
    return camel_row(row)


def delete_document(db: Session, document_id: int) -> None:
    doc = get_document(db, document_id)
    db.execute(text("DELETE FROM document_chunks WHERE document_id = :id"), {"id": document_id})
    db.execute(text("DELETE FROM documents WHERE id = :id"), {"id": document_id})
    file_path = Path(doc["filePath"])
    if file_path.exists():
        file_path.unlink()
    refresh_knowledge_base_counts(db, int(doc["knowledgeBaseId"]))
    db.commit()


def refresh_knowledge_base_counts(db: Session, kb_id: int) -> None:
    db.execute(
        text(
            """
            UPDATE knowledge_bases
            SET document_count = (SELECT COUNT(1) FROM documents WHERE knowledge_base_id = :id),
                chunk_count = (SELECT COUNT(1) FROM document_chunks WHERE knowledge_base_id = :id),
                update_time = NOW()
            WHERE id = :id
            """
        ),
        {"id": kb_id},
    )


def generate_outline(db: Session, kb_id: int) -> list[dict]:
    get_knowledge_base(db, kb_id)
    chunks = get_chunks(db, kb_id)
    if not chunks:
        raise ValueError("Please upload and parse course documents first.")

    db.execute(text("DELETE FROM chapter_progress WHERE chapter_id IN (SELECT id FROM course_chapters WHERE knowledge_base_id = :kb_id)"), {"kb_id": kb_id})
    db.execute(text("DELETE FROM questions WHERE chapter_id IN (SELECT id FROM course_chapters WHERE knowledge_base_id = :kb_id)"), {"kb_id": kb_id})
    db.execute(text("DELETE FROM course_chapters WHERE knowledge_base_id = :kb_id"), {"kb_id": kb_id})

    chapter_count = min(max((len(chunks) + 1) // 2, 1), 5)
    groups = [chunks[index::chapter_count] for index in range(chapter_count)]

    for chapter_index, group in enumerate(groups, start=1):
        joined = "\n".join(group)
        keywords = pick_keywords(joined, 3)
        title = f"第{chapter_index}章 {keywords[0] if keywords else '核心内容'}"
        result = db.execute(
            text(
                """
                INSERT INTO course_chapters (knowledge_base_id, parent_id, title, summary, sort_no)
                VALUES (:kb_id, 0, :title, :summary, :sort_no)
                """
            ),
            {"kb_id": kb_id, "title": title, "summary": summarize_text(joined), "sort_no": chapter_index},
        )
        parent_id = int(result.lastrowid)
        section_titles = keywords[1:] or ["重点概念", "实践应用"]
        for section_index, section_title in enumerate(section_titles[:2], start=1):
            db.execute(
                text(
                    """
                    INSERT INTO course_chapters (knowledge_base_id, parent_id, title, summary, sort_no)
                    VALUES (:kb_id, :parent_id, :title, :summary, :sort_no)
                    """
                ),
                {
                    "kb_id": kb_id,
                    "parent_id": parent_id,
                    "title": f"{chapter_index}.{section_index} {section_title}",
                    "summary": summarize_text(joined, 180),
                    "sort_no": section_index,
                },
            )
    db.commit()
    return list_chapters(db, kb_id)


def list_chapters(db: Session, kb_id: int) -> list[dict]:
    rows = db.execute(
        text(
            """
            SELECT id, knowledge_base_id, parent_id, title, summary, sort_no, create_time, update_time
            FROM course_chapters
            WHERE knowledge_base_id = :kb_id
            ORDER BY parent_id ASC, sort_no ASC, id ASC
            """
        ),
        {"kb_id": kb_id},
    )
    return [camel_row(row) for row in rows]


def get_chunks(db: Session, kb_id: int) -> list[str]:
    rows = db.execute(
        text(
            """
            SELECT content
            FROM document_chunks
            WHERE knowledge_base_id = :kb_id
            ORDER BY document_id ASC, chunk_index ASC
            """
        ),
        {"kb_id": kb_id},
    )
    return [row._mapping["content"] for row in rows]


def get_chapter_content(db: Session, chapter_id: int) -> dict:
    chapter = get_chapter(db, chapter_id)
    chunks = get_chunks(db, int(chapter["knowledgeBaseId"]))
    source = "\n".join(chunks[:3])
    return {
        **chapter,
        "content": [
            {"title": "学习目标", "text": f"理解「{chapter['title']}」相关概念，并能完成基础测验。"},
            {"title": "知识要点", "text": summarize_text(source, 500)},
            {"title": "学习建议", "text": "先阅读本节摘要，再完成自动测验；答错的题目会进入错题本。"},
        ],
    }


def get_chapter(db: Session, chapter_id: int) -> dict:
    row = db.execute(
        text(
            """
            SELECT id, knowledge_base_id, parent_id, title, summary, sort_no, create_time, update_time
            FROM course_chapters
            WHERE id = :id
            """
        ),
        {"id": chapter_id},
    ).first()
    if row is None:
        raise ValueError("Chapter not found.")
    return camel_row(row)


def set_progress(db: Session, chapter_id: int, status: str) -> dict:
    if status not in {"not_started", "learning", "completed"}:
        raise ValueError("Invalid progress status.")
    get_chapter(db, chapter_id)
    db.execute(
        text(
            """
            INSERT INTO chapter_progress (user_id, chapter_id, status, completed_time)
            VALUES (:user_id, :chapter_id, :status, IF(:status = 'completed', NOW(), NULL))
            ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                completed_time = IF(VALUES(status) = 'completed', NOW(), NULL),
                update_time = NOW()
            """
        ),
        {"user_id": DEFAULT_USER_ID, "chapter_id": chapter_id, "status": status},
    )
    db.commit()
    return get_progress(db, chapter_id)


def get_progress(db: Session, chapter_id: int) -> dict:
    row = db.execute(
        text(
            """
            SELECT id, user_id, chapter_id, status, completed_time, create_time, update_time
            FROM chapter_progress
            WHERE user_id = :user_id AND chapter_id = :chapter_id
            """
        ),
        {"user_id": DEFAULT_USER_ID, "chapter_id": chapter_id},
    ).first()
    if row is None:
        return {"chapterId": chapter_id, "status": "not_started"}
    return camel_row(row)


def progress_overview(db: Session, kb_id: int) -> dict:
    total = db.execute(text("SELECT COUNT(1) FROM course_chapters WHERE knowledge_base_id = :kb_id"), {"kb_id": kb_id}).scalar_one()
    completed = db.execute(
        text(
            """
            SELECT COUNT(1)
            FROM chapter_progress p
            JOIN course_chapters c ON c.id = p.chapter_id
            WHERE c.knowledge_base_id = :kb_id AND p.user_id = :user_id AND p.status = 'completed'
            """
        ),
        {"kb_id": kb_id, "user_id": DEFAULT_USER_ID},
    ).scalar_one()
    percent = round((completed / total) * 100, 1) if total else 0
    return {"total": int(total), "completed": int(completed), "percent": percent}


def reset_progress(db: Session, kb_id: int) -> None:
    db.execute(
        text(
            """
            DELETE p
            FROM chapter_progress p
            JOIN course_chapters c ON c.id = p.chapter_id
            WHERE c.knowledge_base_id = :kb_id AND p.user_id = :user_id
            """
        ),
        {"kb_id": kb_id, "user_id": DEFAULT_USER_ID},
    )
    db.commit()


def generate_questions(db: Session, chapter_id: int, difficulty: str = "medium", count: int = 5) -> list[dict]:
    chapter = get_chapter(db, chapter_id)
    chunks = get_chunks(db, int(chapter["knowledgeBaseId"]))
    source_chunks = chunks[: max(count, 1)] or [chapter.get("summary") or chapter["title"]]

    db.execute(text("DELETE FROM questions WHERE chapter_id = :chapter_id"), {"chapter_id": chapter_id})
    for index in range(count):
        question = make_question_from_text(source_chunks[index % len(source_chunks)], index + 1, difficulty)
        db.execute(
            text(
                """
                INSERT INTO questions (chapter_id, question_type, difficulty, stem, options_json, answer, analysis)
                VALUES (:chapter_id, :question_type, :difficulty, :stem, :options_json, :answer, :analysis)
                """
            ),
            {
                "chapter_id": chapter_id,
                "question_type": question["questionType"],
                "difficulty": question["difficulty"],
                "stem": question["stem"],
                "options_json": json.dumps(question["options"], ensure_ascii=False),
                "answer": question["answer"],
                "analysis": question["analysis"],
            },
        )
    db.commit()
    return list_questions(db, chapter_id)


def list_questions(db: Session, chapter_id: int) -> list[dict]:
    rows = db.execute(
        text(
            """
            SELECT id, chapter_id, question_type, difficulty, stem, options_json, answer, analysis, create_time
            FROM questions
            WHERE chapter_id = :chapter_id
            ORDER BY id ASC
            """
        ),
        {"chapter_id": chapter_id},
    )
    questions = []
    for row in rows:
        item = camel_row(row)
        item["options"] = json.loads(item.pop("optionsJson") or "[]")
        questions.append(item)
    return questions


def submit_quiz(db: Session, chapter_id: int, answers: list[dict], duration_seconds: int = 0) -> dict:
    questions = {item["id"]: item for item in list_questions(db, chapter_id)}
    correct_count = 0
    details = []
    for answer in answers:
        question = questions.get(int(answer["questionId"]))
        if not question:
            continue
        user_answer = str(answer.get("userAnswer") or "")
        is_correct = user_answer == str(question["answer"])
        correct_count += 1 if is_correct else 0
        details.append({"question": question, "userAnswer": user_answer, "isCorrect": is_correct})

    total = len(details)
    score = round((correct_count / total) * 100, 2) if total else 0
    result = db.execute(
        text(
            """
            INSERT INTO quiz_attempts (user_id, chapter_id, score, duration_seconds, total_count, correct_count)
            VALUES (:user_id, :chapter_id, :score, :duration, :total, :correct)
            """
        ),
        {
            "user_id": DEFAULT_USER_ID,
            "chapter_id": chapter_id,
            "score": score,
            "duration": duration_seconds,
            "total": total,
            "correct": correct_count,
        },
    )
    attempt_id = int(result.lastrowid)
    for detail in details:
        question = detail["question"]
        db.execute(
            text(
                """
                INSERT INTO quiz_answers (attempt_id, question_id, user_answer, is_correct)
                VALUES (:attempt_id, :question_id, :user_answer, :is_correct)
                """
            ),
            {
                "attempt_id": attempt_id,
                "question_id": question["id"],
                "user_answer": detail["userAnswer"],
                "is_correct": 1 if detail["isCorrect"] else 0,
            },
        )
        if detail["isCorrect"]:
            db.execute(
                text(
                    """
                    UPDATE wrong_questions
                    SET correct_count = correct_count + 1, update_time = NOW()
                    WHERE user_id = :user_id AND question_id = :question_id
                    """
                ),
                {"user_id": DEFAULT_USER_ID, "question_id": question["id"]},
            )
        else:
            db.execute(
                text(
                    """
                    INSERT INTO wrong_questions (user_id, question_id, wrong_count, last_wrong_time)
                    VALUES (:user_id, :question_id, 1, NOW())
                    ON DUPLICATE KEY UPDATE wrong_count = wrong_count + 1, last_wrong_time = NOW(), update_time = NOW()
                    """
                ),
                {"user_id": DEFAULT_USER_ID, "question_id": question["id"]},
            )
    db.commit()
    return {"attemptId": attempt_id, "score": score, "total": total, "correct": correct_count, "details": details}


def quiz_history(db: Session) -> list[dict]:
    rows = db.execute(
        text(
            """
            SELECT a.id, a.chapter_id, c.title AS chapter_title, a.score, a.duration_seconds,
                   a.total_count, a.correct_count, a.create_time
            FROM quiz_attempts a
            JOIN course_chapters c ON c.id = a.chapter_id
            WHERE a.user_id = :user_id
            ORDER BY a.create_time DESC
            LIMIT 30
            """
        ),
        {"user_id": DEFAULT_USER_ID},
    )
    return [camel_row(row) for row in rows]


def wrong_question_list(db: Session) -> list[dict]:
    rows = db.execute(
        text(
            """
            SELECT w.id, w.question_id, q.chapter_id, c.title AS chapter_title, q.difficulty,
                   q.stem, q.options_json, q.answer, q.analysis, w.wrong_count,
                   w.correct_count, w.last_wrong_time, w.update_time
            FROM wrong_questions w
            JOIN questions q ON q.id = w.question_id
            JOIN course_chapters c ON c.id = q.chapter_id
            WHERE w.user_id = :user_id
            ORDER BY w.update_time DESC
            """
        ),
        {"user_id": DEFAULT_USER_ID},
    )
    result = []
    for row in rows:
        item = camel_row(row)
        item["options"] = json.loads(item.pop("optionsJson") or "[]")
        attempts = int(item["wrongCount"]) + int(item["correctCount"])
        item["accuracy"] = round((int(item["correctCount"]) / attempts) * 100, 1) if attempts else 0
        result.append(item)
    return result


def search_chunks(db: Session, kb_id: int, keyword: str) -> list[dict]:
    rows = db.execute(
        text(
            """
            SELECT id, document_id, knowledge_base_id, chunk_index, content, create_time
            FROM document_chunks
            WHERE knowledge_base_id = :kb_id AND content LIKE :keyword
            ORDER BY document_id ASC, chunk_index ASC
            LIMIT 20
            """
        ),
        {"kb_id": kb_id, "keyword": f"%{keyword}%"},
    )
    results = []
    for row in rows:
        item = camel_row(row)
        item["preview"] = summarize_text(re.sub(r"\s+", " ", item["content"]), 180)
        results.append(item)
    return results
