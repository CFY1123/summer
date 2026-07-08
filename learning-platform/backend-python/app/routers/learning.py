from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ok
from app.services import learning_service as service


router = APIRouter(tags=["learning-platform"])


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class ProgressUpdate(BaseModel):
    status: str


class GenerateQuestionsRequest(BaseModel):
    difficulty: str = "medium"
    count: int = Field(default=5, ge=5, le=20)


class QuizAnswer(BaseModel):
    questionId: int
    userAnswer: str


class SubmitQuizRequest(BaseModel):
    answers: list[QuizAnswer]
    durationSeconds: int = 0


def _handle(action):
    try:
        return ok(action())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/knowledge-bases")
def list_knowledge_bases(db: Session = Depends(get_db)) -> dict:
    return ok(service.list_knowledge_bases(db))


@router.post("/knowledge-bases")
def create_knowledge_base(payload: KnowledgeBaseCreate, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.create_knowledge_base(db, payload.name, payload.description))


@router.delete("/knowledge-bases/{kb_id}")
def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.delete_knowledge_base(db, kb_id))


@router.get("/knowledge-bases/{kb_id}/documents")
def list_documents(kb_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.list_documents(db, kb_id))


@router.post("/knowledge-bases/{kb_id}/documents")
def upload_document(kb_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.save_uploaded_document(db, kb_id, file))


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.delete_document(db, document_id))


@router.get("/knowledge-bases/{kb_id}/search")
def search_chunks(kb_id: int, keyword: str, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.search_chunks(db, kb_id, keyword))


@router.post("/knowledge-bases/{kb_id}/outline")
def generate_outline(kb_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.generate_outline(db, kb_id))


@router.get("/knowledge-bases/{kb_id}/chapters")
def list_chapters(kb_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.list_chapters(db, kb_id))


@router.get("/chapters/{chapter_id}/content")
def chapter_content(chapter_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.get_chapter_content(db, chapter_id))


@router.patch("/chapters/{chapter_id}/progress")
def update_progress(chapter_id: int, payload: ProgressUpdate, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.set_progress(db, chapter_id, payload.status))


@router.get("/knowledge-bases/{kb_id}/progress")
def progress_overview(kb_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.progress_overview(db, kb_id))


@router.delete("/knowledge-bases/{kb_id}/progress")
def reset_progress(kb_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.reset_progress(db, kb_id))


@router.post("/chapters/{chapter_id}/questions")
def generate_questions(chapter_id: int, payload: GenerateQuestionsRequest, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.generate_questions(db, chapter_id, payload.difficulty, payload.count))


@router.get("/chapters/{chapter_id}/questions")
def list_questions(chapter_id: int, db: Session = Depends(get_db)) -> dict:
    return _handle(lambda: service.list_questions(db, chapter_id))


@router.post("/chapters/{chapter_id}/quiz")
def submit_quiz(chapter_id: int, payload: SubmitQuizRequest, db: Session = Depends(get_db)) -> dict:
    answers = [answer.model_dump() for answer in payload.answers]
    return _handle(lambda: service.submit_quiz(db, chapter_id, answers, payload.durationSeconds))


@router.get("/quiz/history")
def quiz_history(db: Session = Depends(get_db)) -> dict:
    return ok(service.quiz_history(db))


@router.get("/wrong-questions")
def wrong_questions(db: Session = Depends(get_db)) -> dict:
    return ok(service.wrong_question_list(db))
