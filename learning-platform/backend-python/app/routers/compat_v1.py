import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import Response, StreamingResponse

from app.services.face_auth_service import FaceAuthError, login_with_face, register_face


router = APIRouter(prefix="/api/v1", tags=["ai-learn-web-compatible"])

QUESTION_TYPES = ["AI Agent", "RAG", "LangChain", "Vector DB", "Prompt"]
QUESTIONS = [
    {
        "id": "1",
        "code": "Q001",
        "question": "What problem does RAG solve in LLM applications?",
        "questionType": "RAG",
        "questionTypeText": "RAG",
        "importanceScore": 96,
        "occurrenceCount": 18,
        "createdAt": "2026-07-08 09:00:00",
        "standardAnswer": "RAG retrieves relevant knowledge before generation, reducing hallucination and enabling private knowledge QA.",
    },
    {
        "id": "2",
        "code": "Q002",
        "question": "What is LangChain usually used for?",
        "questionType": "LangChain",
        "questionTypeText": "LangChain",
        "importanceScore": 90,
        "occurrenceCount": 15,
        "createdAt": "2026-07-08 09:10:00",
        "standardAnswer": "LangChain organizes models, prompts, tools, memory, retrievers, and chains for LLM application development.",
    },
    {
        "id": "3",
        "code": "Q003",
        "question": "Why is a vector database useful for semantic search?",
        "questionType": "Vector DB",
        "questionTypeText": "Vector DB",
        "importanceScore": 88,
        "occurrenceCount": 12,
        "createdAt": "2026-07-08 09:20:00",
        "standardAnswer": "It stores embeddings and finds semantically similar content through vector similarity.",
    },
    {
        "id": "4",
        "code": "Q004",
        "question": "Why should prompts define role, task, and output format?",
        "questionType": "Prompt",
        "questionTypeText": "Prompt",
        "importanceScore": 82,
        "occurrenceCount": 10,
        "createdAt": "2026-07-08 09:30:00",
        "standardAnswer": "Clear prompts reduce ambiguity and make model output more stable and easier to integrate.",
    },
]

COMMENTS: list[dict[str, Any]] = []
SUGGESTIONS: list[dict[str, Any]] = []


def success(data: Any = None) -> dict[str, Any]:
    return {"code": "SUCCESS", "message": "success", "data": data, "traceId": "local-dev"}


def current_user() -> dict[str, Any]:
    return {
        "id": "1",
        "username": "admin",
        "nickname": "Learner",
        "avatar": None,
        "gender": None,
        "motto": "Build a runnable prototype first, then improve AI features.",
        "email": "admin@example.com",
        "experience": 120,
        "level": "LV1",
        "levelName": "Starter",
        "rank": "Bronze",
        "levelValue": 1,
        "currentLevelExperience": 120,
        "nextLevelExperience": 300,
        "experienceToNextLevel": 180,
        "levelProgressText": "120 / 300",
        "superAdmin": False,
        "createdAt": "2026-07-08 09:00:00",
    }


def growth_info() -> dict[str, Any]:
    return {
        "earnedExperience": 0,
        "currentExperience": 120,
        "level": "LV1",
        "levelName": "Starter",
        "rank": "Bronze",
        "levelValue": 1,
        "currentLevelExperience": 120,
        "nextLevelExperience": 300,
        "levelProgressText": "120 / 300",
        "answeredCount": 3,
        "averageScore": 82,
        "experienceToNextLevel": 180,
        "streakDays": 1,
        "badges": [
            {
                "id": "first-login",
                "name": "First Step",
                "description": "Signed in for the first time.",
                "icon": "Star",
                "ruleCode": "FIRST_LOGIN",
                "category": "ENTRY",
                "categoryName": "Entry",
                "hidden": False,
                "acquired": True,
                "acquiredAt": "2026-07-08 09:00:00",
            }
        ],
        "newBadges": [],
    }


def page(records: list[dict[str, Any]], page_no: int = 1, page_size: int = 10) -> dict[str, Any]:
    start = max(page_no - 1, 0) * page_size
    end = start + page_size
    return {"records": records[start:end], "pageNo": page_no, "pageSize": page_size, "total": len(records)}


def parse_page_params(request: Request) -> tuple[int, int]:
    page_no = int(request.query_params.get("pageNo", "1"))
    page_size = int(request.query_params.get("pageSize", "10"))
    return page_no, page_size


@router.post("/auth/login")
@router.post("/auth/register")
async def login() -> dict[str, Any]:
    return success({"accessToken": "local-dev-token", "tokenType": "Bearer", "expiresIn": 86400, "user": current_user()})


@router.post("/auth/logout")
async def logout() -> dict[str, Any]:
    return success(True)


@router.post("/auth/face/register")
async def face_register(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        username = payload.get("username") or "admin"
        result = register_face(username, payload["frame"], payload["livenessFrame"])
        return success(result)
    except FaceAuthError as exc:
        return {"code": str(exc), "message": str(exc), "data": None, "traceId": "local-dev"}


@router.post("/auth/face/login")
async def face_login(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        username = payload.get("username") or "admin"
        login_with_face(username, payload["frame"], payload["livenessFrame"])
        return await login()
    except FaceAuthError as exc:
        return {"code": str(exc), "message": str(exc), "data": None, "traceId": "local-dev"}


@router.get("/users/me")
async def users_me() -> dict[str, Any]:
    return success(current_user())


@router.put("/users/me/profile")
async def update_profile(payload: dict[str, Any]) -> dict[str, Any]:
    user = current_user()
    user.update({key: value for key, value in payload.items() if key in {"nickname", "gender", "motto"}})
    return success(user)


@router.get("/users/me/question-stats")
async def user_question_stats(request: Request) -> dict[str, Any]:
    page_no, page_size = parse_page_params(request)
    records = [
        {
            "questionCode": item["code"],
            "question": item["question"],
            "questionType": item["questionType"],
            "answerCount": 1,
            "bestScore": 85,
            "lastScore": 85,
            "firstAnsweredAt": "2026-07-08 10:00:00",
            "lastAnsweredAt": "2026-07-08 10:00:00",
        }
        for item in QUESTIONS
    ]
    return success(page(records, page_no, page_size))


@router.get("/users/me/question-stats/overview")
async def user_question_stats_overview() -> dict[str, Any]:
    return success(
        {
            "practicedQuestionCount": 3,
            "totalAnswerCount": 3,
            "averageBestScore": 85,
            "averageLastScore": 82,
            "weakQuestionCount": 1,
            "lastAnsweredAt": "2026-07-08 10:00:00",
            "questionTypes": QUESTION_TYPES,
            "typeStats": [
                {
                    "questionType": item,
                    "questionCount": 1,
                    "answerCount": 1,
                    "averageBestScore": 85,
                    "averageLastScore": 82,
                    "weakCount": 0,
                }
                for item in QUESTION_TYPES[:3]
            ],
        }
    )


@router.get("/growth/me")
async def growth_me() -> dict[str, Any]:
    return success(growth_info())


@router.get("/model-entitlements/status")
async def model_entitlement_status() -> dict[str, Any]:
    return success(
        {
            "level": "BASIC",
            "levelText": "Basic",
            "modelName": "local-rule-engine",
            "remainingDays": 999,
            "remainingDaysText": "Local development",
            "permanent": True,
            "authorizationVisible": False,
            "authorizationButtonText": "Enabled",
            "authorizationUrl": "",
            "authorizationConfigured": False,
            "frozenTip": "",
            "frozenProRemainingDays": 0,
        }
    )


@router.post("/model-entitlements/redeem")
async def redeem_model_code() -> dict[str, Any]:
    result = (await model_entitlement_status())["data"]
    return success({"message": "Local development mode is enabled.", "entitlement": result})


@router.get("/practice/categories")
async def practice_categories() -> dict[str, Any]:
    return success(QUESTION_TYPES)


@router.get("/practice/state")
async def practice_state() -> dict[str, Any]:
    return success(
        {
            "phase": "QUESTIONING",
            "phaseText": "Waiting",
            "currentQuestion": None,
            "lastScore": None,
            "questionTypes": QUESTION_TYPES,
            "messages": [{"role": "assistant", "text": "Choose a category and start practicing.", "question": None, "grading": None}],
            "growth": growth_info(),
        }
    )


@router.post("/practice/next-question")
@router.post("/practice/retry")
async def next_practice_question(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    selected = (payload or {}).get("questionTypes") or QUESTION_TYPES
    question = next((item for item in QUESTIONS if item["questionType"] in selected), QUESTIONS[0])
    practice_question = {
        "code": question["code"],
        "question": question["question"],
        "questionType": question["questionType"],
        "importanceScore": question["importanceScore"],
        "occurrenceCount": question["occurrenceCount"],
        "answeredCount": 0,
        "bestScore": 0,
    }
    return success(
        {
            "action": "QUESTION",
            "phase": "ANSWERING",
            "message": question["question"],
            "question": practice_question,
            "grading": None,
            "growth": growth_info(),
        }
    )


def grading_result(content: str) -> dict[str, Any]:
    score = 85 if len(content.strip()) > 20 else 65
    return {
        "score": score,
        "hitPoints": ["Core concept mentioned", "Application scenario mentioned"],
        "missingPoints": ["Add implementation steps", "Add edge cases"],
        "problems": [] if score >= 80 else ["Answer is a bit short"],
        "referenceAnswer": QUESTIONS[0]["standardAnswer"],
        "improvementAdvice": "Use a definition-effect-example structure.",
        "earnedExperience": 10,
        "previousBestScore": 0,
        "previousLastScore": None,
        "experienceDetail": "Practice completed +10",
        "totalExperience": 130,
        "newBadges": [],
        "fallbackUsed": False,
    }


@router.post("/practice/messages/stream")
async def practice_message_stream(payload: dict[str, Any]) -> StreamingResponse:
    content = payload.get("content", "")
    grading = grading_result(content)
    result = {
        "action": "GRADING",
        "phase": "DISCUSSING",
        "message": grading["improvementAdvice"],
        "question": None,
        "grading": grading,
        "growth": growth_info(),
    }

    async def events():
        yield "event: message\ndata: Grading your answer...\n\n"
        yield f"event: result\ndata: {json.dumps(result)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/questions/types")
@router.get("/public/questions/types")
@router.get("/admin/system-questions/types")
async def question_types() -> dict[str, Any]:
    return success(QUESTION_TYPES)


@router.get("/questions")
@router.get("/admin/system-questions")
async def questions(request: Request) -> dict[str, Any]:
    page_no, page_size = parse_page_params(request)
    keyword = request.query_params.get("keyword", "")
    question_type = request.query_params.get("questionType", "")
    records = [
        item
        for item in QUESTIONS
        if (not keyword or keyword.lower() in item["question"].lower()) and (not question_type or question_type == item["questionType"])
    ]
    return success(page(records, page_no, page_size))


@router.get("/questions/{question_id}")
async def question_detail(question_id: str) -> dict[str, Any]:
    return success(next((item for item in QUESTIONS if item["id"] == question_id), QUESTIONS[0]))


@router.get("/public/questions/interview-document")
async def interview_document(request: Request) -> dict[str, Any]:
    question_type = request.query_params.get("questionType", "")
    records = [item for item in QUESTIONS if not question_type or item["questionType"] == question_type]
    return success(records)


def interaction_item(kind: str, content: str) -> dict[str, Any]:
    return {
        "id": f"{kind}-{datetime.now().timestamp()}",
        "content": content,
        "username": "admin",
        "nickname": "Learner",
        "likeCount": 0,
        "liked": False,
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@router.get("/comments")
async def list_comments(request: Request) -> dict[str, Any]:
    page_no, page_size = parse_page_params(request)
    return success(page(COMMENTS, page_no, page_size))


@router.post("/comments")
async def create_comment(payload: dict[str, Any]) -> dict[str, Any]:
    item = interaction_item("comment", payload.get("content", ""))
    COMMENTS.insert(0, item)
    return success(item)


@router.post("/comments/{comment_id}/like")
async def like_comment(comment_id: str) -> dict[str, Any]:
    item = next((comment for comment in COMMENTS if comment["id"] == comment_id), interaction_item("comment", "Local comment"))
    item["liked"] = not item.get("liked", False)
    item["likeCount"] = max(0, int(item.get("likeCount", 0)) + (1 if item["liked"] else -1))
    return success(item)


@router.get("/suggestions")
async def list_suggestions(request: Request) -> dict[str, Any]:
    page_no, page_size = parse_page_params(request)
    return success(page(SUGGESTIONS, page_no, page_size))


@router.post("/suggestions")
async def create_suggestion(payload: dict[str, Any]) -> dict[str, Any]:
    item = interaction_item("suggestion", payload.get("content", ""))
    item["title"] = payload.get("title", "Learning platform suggestion")
    SUGGESTIONS.insert(0, item)
    return success(item)


@router.post("/suggestions/{suggestion_id}/like")
async def like_suggestion(suggestion_id: str) -> dict[str, Any]:
    item = next((suggestion for suggestion in SUGGESTIONS if suggestion["id"] == suggestion_id), interaction_item("suggestion", "Local suggestion"))
    item["liked"] = not item.get("liked", False)
    item["likeCount"] = max(0, int(item.get("likeCount", 0)) + (1 if item["liked"] else -1))
    return success(item)


@router.get("/admin/users")
async def admin_users(request: Request) -> dict[str, Any]:
    page_no, page_size = parse_page_params(request)
    return success(page([current_user()], page_no, page_size))


@router.get("/admin/users/limit")
@router.put("/admin/users/limit")
async def user_limit() -> dict[str, Any]:
    return success({"maxUsers": 100, "currentUsers": 1})


@router.post("/admin/users")
@router.put("/admin/users/{user_id}")
async def save_admin_user(payload: dict[str, Any]) -> dict[str, Any]:
    user = current_user()
    user.update(payload)
    return success(user)


@router.delete("/admin/users/{user_id}")
async def delete_admin_user(user_id: str) -> dict[str, Any]:
    return success(True)


@router.delete("/admin/system-questions/clear")
async def clear_system_questions() -> dict[str, Any]:
    return success(True)


@router.post("/admin/system-questions")
@router.put("/admin/system-questions/{question_id}")
async def save_system_question(payload: dict[str, Any]) -> dict[str, Any]:
    item = {**QUESTIONS[0], **payload, "id": payload.get("id", "local")}
    return success(item)


@router.delete("/admin/system-questions/{question_id}")
async def delete_system_question(question_id: str) -> dict[str, Any]:
    return success(True)


@router.get("/admin/system-questions/template")
async def system_question_template() -> Response:
    return Response("code,question,questionType,standardAnswer\n", media_type="text/csv")


@router.post("/admin/system-questions/import/precheck")
@router.post("/admin/system-questions/import")
async def import_questions(file: UploadFile = File(...)) -> dict[str, Any]:
    return success({"successCount": 0, "failCount": 0, "errors": [], "filename": file.filename})


@router.get("/admin/redemption-codes")
async def redemption_codes(request: Request) -> dict[str, Any]:
    page_no, page_size = parse_page_params(request)
    return success(page([], page_no, page_size))


@router.post("/admin/redemption-codes/generate")
async def generate_codes() -> dict[str, Any]:
    return success([])


@router.get("/admin/redemption-codes/export")
async def export_codes() -> Response:
    return Response("code,status\n", media_type="text/csv")


@router.get("/admin/model-configs")
async def model_configs() -> dict[str, Any]:
    return success([])


@router.post("/admin/model-configs")
@router.put("/admin/model-configs/{config_id}")
async def save_model_config(payload: dict[str, Any]) -> dict[str, Any]:
    return success(payload)


@router.get("/admin/log-levels")
async def log_levels() -> dict[str, Any]:
    return success([])


@router.put("/admin/log-levels")
async def save_log_levels(payload: Any) -> dict[str, Any]:
    return success(payload)
