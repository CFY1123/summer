from fastapi import APIRouter

from app.schemas.common import ok


router = APIRouter(prefix="/project", tags=["project"])


@router.get("")
def project_overview() -> dict:
    return ok(
        {
            "name": "AI 学习助手",
            "activeModules": [
                "本地知识库构建",
                "课程大纲梳理",
                "章节学习进度",
                "在线测验",
                "错题复盘",
            ],
            "deferredModules": [
                "人脸识别登录",
                "语音交互模式",
            ],
            "database": "learning_platform",
        }
    )
