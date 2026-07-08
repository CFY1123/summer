import base64
import json
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

from app.core.config import ROOT_DIR


TEMPLATE_FILE = ROOT_DIR / "storage" / "face_templates.json"
HASH_SIZE = 8
MAX_DISTANCE = 28
MIN_LIVENESS_SCORE = 2.0


class FaceAuthError(ValueError):
    pass


def register_face(username: str, frame: str, liveness_frame: str) -> dict[str, Any]:
    _check_liveness(frame, liveness_frame)
    templates = _load_templates()
    templates[username] = {
        "hash": _image_hash(frame),
        "hashSize": HASH_SIZE,
    }
    _save_templates(templates)
    return {"username": username, "registered": True}


def login_with_face(username: str, frame: str, liveness_frame: str) -> dict[str, Any]:
    _check_liveness(frame, liveness_frame)
    templates = _load_templates()
    template = templates.get(username)
    if not template:
        raise FaceAuthError("FACE_NOT_REGISTERED")

    current_hash = _image_hash(frame)
    distance = _hamming_distance(current_hash, template["hash"])
    if distance > MAX_DISTANCE:
        raise FaceAuthError("FACE_MISMATCH")

    return {"username": username, "matched": True, "distance": distance}


def _check_liveness(frame: str, liveness_frame: str) -> None:
    score = _frame_difference(frame, liveness_frame)
    if score < MIN_LIVENESS_SCORE:
        raise FaceAuthError("LIVENESS_CHECK_FAILED")


def _load_templates() -> dict[str, Any]:
    if not TEMPLATE_FILE.exists():
        return {}
    return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))


def _save_templates(templates: dict[str, Any]) -> None:
    TEMPLATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE_FILE.write_text(json.dumps(templates, indent=2), encoding="utf-8")


def _decode_image(data_url: str) -> Image.Image:
    payload = data_url.split(",", 1)[1] if "," in data_url else data_url
    raw = base64.b64decode(payload)
    return Image.open(BytesIO(raw)).convert("RGB")


def _image_hash(data_url: str) -> str:
    image = _decode_image(data_url).convert("L").resize((HASH_SIZE, HASH_SIZE))
    pixels = list(image.getdata())
    average = sum(pixels) / len(pixels)
    return "".join("1" if pixel >= average else "0" for pixel in pixels)


def _frame_difference(first: str, second: str) -> float:
    first_image = _decode_image(first).convert("L").resize((64, 64))
    second_image = _decode_image(second).convert("L").resize((64, 64))
    diff = ImageChops.difference(first_image, second_image)
    return float(ImageStat.Stat(diff).mean[0])


def _hamming_distance(left: str, right: str) -> int:
    return sum(1 for a, b in zip(left, right) if a != b) + abs(len(left) - len(right))
