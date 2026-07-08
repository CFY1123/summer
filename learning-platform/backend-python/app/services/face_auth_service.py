import base64
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from app.core.config import ROOT_DIR


TEMPLATE_FILE = ROOT_DIR / "storage" / "face_templates.json"
FEATURE_VERSION = 2
FACE_SIZE = 96
PIXEL_SIZE = 32
MIN_LIVENESS_SCORE = 1.5
MAX_PIXEL_DISTANCE = 0.22
MAX_HIST_DISTANCE = 0.42
MAX_HASH_DISTANCE = 86


class FaceAuthError(ValueError):
    pass


@dataclass
class FaceFeature:
    pixels: list[float]
    hist: list[float]
    hash: str
    face_box: list[int]


def register_face(username: str, frame: str, liveness_frame: str) -> dict[str, Any]:
    if not username:
        raise FaceAuthError("USERNAME_REQUIRED")

    feature = _extract_face_feature(frame)
    _check_liveness(frame, liveness_frame)
    templates = _load_templates()
    templates[username] = {
        "version": FEATURE_VERSION,
        "pixels": feature.pixels,
        "hist": feature.hist,
        "hash": feature.hash,
        "faceBox": feature.face_box,
    }
    _save_templates(templates)
    return {"username": username, "registered": True}


def login_with_face(username: str, frame: str, liveness_frame: str) -> dict[str, Any]:
    if not username:
        raise FaceAuthError("USERNAME_REQUIRED")

    _check_liveness(frame, liveness_frame)
    templates = _load_templates()
    template = templates.get(username)
    if not template:
        raise FaceAuthError("FACE_NOT_REGISTERED")
    if template.get("version") != FEATURE_VERSION:
        raise FaceAuthError("FACE_TEMPLATE_EXPIRED")

    current = _extract_face_feature(frame)
    pixel_distance = _cosine_distance(current.pixels, template["pixels"])
    hist_distance = _hist_distance(current.hist, template["hist"])
    hash_distance = _hamming_distance(current.hash, template["hash"])

    if (
        pixel_distance > MAX_PIXEL_DISTANCE
        or hist_distance > MAX_HIST_DISTANCE
        or hash_distance > MAX_HASH_DISTANCE
    ):
        raise FaceAuthError("FACE_MISMATCH")

    return {
        "username": username,
        "matched": True,
        "pixelDistance": round(pixel_distance, 4),
        "histDistance": round(hist_distance, 4),
        "hashDistance": hash_distance,
    }


def _check_liveness(frame: str, liveness_frame: str) -> None:
    first_face = _extract_face_gray(frame)
    second_face = _extract_face_gray(liveness_frame)
    first_face = cv2.resize(first_face, (FACE_SIZE, FACE_SIZE))
    second_face = cv2.resize(second_face, (FACE_SIZE, FACE_SIZE))
    score = float(np.mean(cv2.absdiff(first_face, second_face)))
    if score < MIN_LIVENESS_SCORE:
        raise FaceAuthError("LIVENESS_CHECK_FAILED")


def _load_templates() -> dict[str, Any]:
    if not TEMPLATE_FILE.exists():
        return {}
    return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))


def _save_templates(templates: dict[str, Any]) -> None:
    TEMPLATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE_FILE.write_text(json.dumps(templates, indent=2), encoding="utf-8")


def _extract_face_feature(data_url: str) -> FaceFeature:
    face = _extract_face_gray(data_url)
    face = cv2.resize(face, (FACE_SIZE, FACE_SIZE))
    face = cv2.equalizeHist(face)

    small = cv2.resize(face, (PIXEL_SIZE, PIXEL_SIZE)).astype(np.float32) / 255.0
    pixels = [round(float(value), 4) for value in small.flatten()]

    hist = cv2.calcHist([face], [0], None, [32], [0, 256])
    cv2.normalize(hist, hist)
    hist_values = [round(float(value), 5) for value in hist.flatten()]

    return FaceFeature(
        pixels=pixels,
        hist=hist_values,
        hash=_difference_hash(face),
        face_box=_detect_face_box(_decode_image(data_url)),
    )


def _extract_face_gray(data_url: str) -> np.ndarray:
    image = _decode_image(data_url)
    box = _detect_face_box(image)
    x, y, width, height = box
    face = image[y : y + height, x : x + width]
    return cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)


def _decode_image(data_url: str) -> np.ndarray:
    payload = data_url.split(",", 1)[1] if "," in data_url else data_url
    raw = base64.b64decode(payload)
    array = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise FaceAuthError("IMAGE_DECODE_FAILED")
    return image


def _detect_face_box(image: np.ndarray) -> list[int]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier(str(_resolve_classifier_path()))
    if detector.empty():
        raise FaceAuthError("FACE_DETECTOR_UNAVAILABLE")
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(70, 70))
    if len(faces) == 0:
        raise FaceAuthError("FACE_NOT_FOUND")

    x, y, width, height = max(faces, key=lambda item: item[2] * item[3])
    return [int(x), int(y), int(width), int(height)]


def _resolve_classifier_path() -> Path:
    source = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    target_dir = Path(tempfile.gettempdir()) / "ai_learning_face"
    target = target_dir / "haarcascade_frontalface_default.xml"
    if not target.exists():
        if not source.exists():
            raise FaceAuthError("FACE_DETECTOR_UNAVAILABLE")
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return target


def _difference_hash(face: np.ndarray) -> str:
    resized = cv2.resize(face, (17, 16))
    diff = resized[:, 1:] > resized[:, :-1]
    return "".join("1" if value else "0" for value in diff.flatten())


def _cosine_distance(left: list[float], right: list[float]) -> float:
    left_vector = np.array(left, dtype=np.float32)
    right_vector = np.array(right, dtype=np.float32)
    denominator = float(np.linalg.norm(left_vector) * np.linalg.norm(right_vector))
    if denominator == 0:
        return 1.0
    similarity = float(np.dot(left_vector, right_vector) / denominator)
    return 1.0 - similarity


def _hist_distance(left: list[float], right: list[float]) -> float:
    left_hist = np.array(left, dtype=np.float32)
    right_hist = np.array(right, dtype=np.float32)
    return float(cv2.compareHist(left_hist, right_hist, cv2.HISTCMP_BHATTACHARYYA))


def _hamming_distance(left: str, right: str) -> int:
    return sum(1 for a, b in zip(left, right) if a != b) + abs(len(left) - len(right))
