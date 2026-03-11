import base64
import hashlib
import hmac
import json
import os
import asyncio
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import BOT_TOKEN, BOT_USERNAME, DATABASE_PATH, MINI_APP_URL
from database import Database
from bot import run_bot_polling


load_dotenv()

app = FastAPI(title="Tinder TG Mini App API", version="1.0.0")
db = Database(DATABASE_PATH)

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "miniapp"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GIFT_CATALOG = {
    "rose": "🌹 Rose",
    "heart": "💖 Heart",
    "cake": "🎂 Cake",
}

SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "86400"))
SESSION_SECRET = os.getenv("SESSION_SECRET", "") or os.getenv("MESSAGE_ENCRYPTION_KEY", "") or BOT_TOKEN
RUN_BOT_IN_PROCESS = os.getenv("RUN_BOT_IN_PROCESS", "1") == "1"

_bot_thread: Optional[threading.Thread] = None


def _build_open_app_markup() -> Optional[InlineKeyboardMarkup]:
    if not MINI_APP_URL:
        return None
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("📱 Open Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]]
    )


def _notify_liked_user(from_user_id: int, to_user_id: int) -> None:
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        return
    if from_user_id == to_user_id:
        return

    from_user = db.get_user(from_user_id)
    from_name = (from_user or {}).get("name") or "Someone"
    text = f"❤️ {from_name} поставил(а) тебе лайк!\n\nУ тебя есть лайк, зайди проверить кто это сделал."

    async def _send() -> None:
        bot = Bot(BOT_TOKEN)
        await bot.send_message(
            chat_id=to_user_id,
            text=text,
            reply_markup=_build_open_app_markup(),
        )
        await bot.close()

    try:
        asyncio.run(_send())
    except Exception:
        pass


class TelegramAuthRequest(BaseModel):
    initData: str


class ProfileUpsertRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    age: int = Field(ge=18, le=100)
    gender: str = Field(pattern="^(male|female)$")
    looking_for: str = Field(pattern="^(male|female)$")
    bio: str = Field(default="", max_length=500)
    city: str = Field(default="", max_length=120)
    photo_id: Optional[str] = Field(default=None, max_length=255)
    min_age: Optional[int] = Field(default=None, ge=18, le=100)
    max_age: Optional[int] = Field(default=None, ge=18, le=100)


class SwipeRequest(BaseModel):
    to_user_id: int
    action: str = Field(pattern="^(like|dislike)$")


class SendMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class SendGiftRequest(BaseModel):
    to_user_id: int
    gift_code: str = Field(pattern="^(rose|heart|cake)$")
    gift_message: str = Field(default="", max_length=250)


def _base64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _create_session_token(claims: Dict[str, Any]) -> str:
    payload = json.dumps(claims, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    encoded_payload = _base64url_encode(payload)
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), encoded_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{encoded_payload}.{signature}"


def _parse_session_token(token: str) -> Dict[str, Any]:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token format") from exc

    expected_signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid token signature")

    try:
        payload = json.loads(_base64url_decode(encoded_payload).decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail="Invalid token payload") from exc

    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="Token expired")

    return payload


def _verify_telegram_init_data(init_data: str) -> Dict[str, Any]:
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise HTTPException(status_code=500, detail="BOT_TOKEN is not configured")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash in initData")

    check_string = "\n".join(f"{key}={pairs[key]}" for key in sorted(pairs.keys()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(received_hash, expected_hash):
        raise HTTPException(status_code=401, detail="Invalid Telegram initData signature")

    auth_date = int(pairs.get("auth_date", "0"))
    if auth_date <= 0:
        raise HTTPException(status_code=401, detail="Invalid auth_date")

    if int(time.time()) - auth_date > SESSION_TTL_SECONDS:
        raise HTTPException(status_code=401, detail="initData expired")

    user_raw = pairs.get("user")
    if not user_raw:
        raise HTTPException(status_code=401, detail="Missing user payload")

    try:
        return json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=401, detail="Invalid user payload") from exc


def _serialize_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "age": user["age"],
        "gender": user["gender"],
        "looking_for": user["looking_for"],
        "bio": user.get("bio") or "",
        "city": user.get("city") or "",
        "photo_id": user.get("photo_id"),
        "min_age": user.get("min_age", 18),
        "max_age": user.get("max_age", 100),
    }


def _serialize_candidate(candidate: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not candidate:
        return None
    return {
        "user_id": candidate["user_id"],
        "name": candidate["name"],
        "age": candidate["age"],
        "bio": candidate.get("bio") or "",
        "city": candidate.get("city") or "",
        "photo_id": candidate.get("photo_id"),
    }


def _get_claims(authorization: Optional[str] = Header(default=None, alias="Authorization")) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    return _parse_session_token(token)


@app.get("/")
def root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.on_event("startup")
def startup_event() -> None:
    global _bot_thread

    if not RUN_BOT_IN_PROCESS:
        return

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        return

    if _bot_thread and _bot_thread.is_alive():
        return

    _bot_thread = threading.Thread(
        target=run_bot_polling,
        kwargs={"in_background_thread": True},
        daemon=True,
        name="telegram-bot-polling",
    )
    _bot_thread.start()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/telegram")
def auth_telegram(payload: TelegramAuthRequest) -> Dict[str, Any]:
    tg_user = _verify_telegram_init_data(payload.initData)
    user_id = int(tg_user["id"])

    now = int(time.time())
    token = _create_session_token(
        {
            "uid": user_id,
            "username": tg_user.get("username", ""),
            "first_name": tg_user.get("first_name", ""),
            "exp": now + SESSION_TTL_SECONDS,
        }
    )

    exists = db.user_exists(user_id)
    profile_complete = db.is_profile_complete(user_id) if exists else False

    return {
        "token": token,
        "user_id": user_id,
        "telegram_user": tg_user,
        "profile_exists": exists,
        "profile_complete": profile_complete,
    }


@app.get("/api/me")
def get_me(claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    user = db.get_user(user_id)
    if not user:
        return {"profile_complete": False, "user": None}

    return {
        "profile_complete": db.is_profile_complete(user_id),
        "user": _serialize_user(user),
    }


@app.post("/api/profile")
def upsert_profile(request: ProfileUpsertRequest, claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    current = db.get_user(user_id)

    username = claims.get("username", "") or None
    first_name = claims.get("first_name", "") or ""
    min_age = request.min_age if request.min_age is not None else (current.get("min_age", 18) if current else 18)
    max_age = request.max_age if request.max_age is not None else (current.get("max_age", 100) if current else 100)
    if min_age > max_age:
        raise HTTPException(status_code=400, detail="min_age must be <= max_age")

    if not current:
        db.create_user(
            user_id=user_id,
            username=username,
            first_name=first_name,
            name=request.name.strip(),
            age=request.age,
            gender=request.gender,
            looking_for=request.looking_for,
            bio=request.bio.strip(),
            photo_id=request.photo_id,
            city=request.city.strip() or None,
            min_age=min_age,
            max_age=max_age,
        )
    else:
        conn = db.get_connection()
        conn.execute(
            """
            UPDATE users
            SET name = ?, age = ?, gender = ?, looking_for = ?, bio = ?, city = ?, photo_id = ?, username = ?, first_name = ?, min_age = ?, max_age = ?
            WHERE user_id = ?
            """,
            (
                request.name.strip(),
                request.age,
                request.gender,
                request.looking_for,
                request.bio.strip(),
                request.city.strip() or None,
                request.photo_id,
                username,
                first_name,
                min_age,
                max_age,
                user_id,
            ),
        )
        conn.commit()
        conn.close()

    user = db.get_user(user_id)
    return {"ok": True, "user": _serialize_user(user)}


@app.post("/api/profile/photo-upload")
async def upload_profile_photo(
    request: Request,
    file: UploadFile = File(...),
    claims: Dict[str, Any] = Depends(_get_claims),
) -> Dict[str, str]:
    _ = claims
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image is too large (max 8MB)")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    file_name = f"{uuid.uuid4().hex}{suffix}"
    out_path = UPLOADS_DIR / file_name
    out_path.write_bytes(content)
    return {"photo_url": str(request.base_url).rstrip("/") + f"/uploads/{file_name}"}


@app.get("/api/feed/next")
def get_feed_next(claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    if not db.is_profile_complete(user_id):
        raise HTTPException(status_code=400, detail="Complete profile first")

    candidate = db.get_next_candidate_for_feed(user_id)
    if candidate:
        db.track_profile_view(user_id, candidate["user_id"])

    return {"candidate": _serialize_candidate(candidate)}


@app.post("/api/swipe")
def swipe(request: SwipeRequest, claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    if not db.is_profile_complete(user_id):
        raise HTTPException(status_code=400, detail="Complete profile first")

    if request.to_user_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot swipe yourself")

    target = db.get_user(request.to_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    db.record_swipe(user_id, request.to_user_id, request.action)

    is_match = False
    if request.action == "like":
        db.update_like_stats(user_id, request.to_user_id)
        is_match = db.add_like(user_id, request.to_user_id)
        _notify_liked_user(user_id, request.to_user_id)
        if is_match:
            db.update_match_stats(user_id, request.to_user_id)

    next_candidate = db.get_next_candidate_for_feed(user_id)
    if next_candidate:
        db.track_profile_view(user_id, next_candidate["user_id"])

    return {
        "ok": True,
        "action": request.action,
        "match": is_match,
        "next_candidate": _serialize_candidate(next_candidate),
    }


@app.get("/api/matches")
def get_matches(claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    matches = db.get_matches(user_id)
    return {
        "matches": [
            {
                "user_id": m["user_id"],
                "name": m["name"],
                "age": m["age"],
                "city": m.get("city") or "",
            }
            for m in matches
        ]
    }


@app.get("/api/likes/inbox-count")
def get_likes_inbox_count(claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, int]:
    user_id = int(claims["uid"])
    likes = db.get_who_liked_me(user_id)
    return {"count": len(likes)}


@app.get("/api/chat/{other_user_id}")
def get_chat(other_user_id: int, claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    if not db.is_match(user_id, other_user_id):
        raise HTTPException(status_code=403, detail="Chat allowed only with matches")

    db.mark_messages_read(user_id, other_user_id)
    messages = db.get_messages(user_id, other_user_id, limit=100)
    return {"messages": messages}


@app.post("/api/chat/{other_user_id}")
def send_chat_message(
    other_user_id: int,
    request: SendMessageRequest,
    claims: Dict[str, Any] = Depends(_get_claims),
) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    if not db.is_match(user_id, other_user_id):
        raise HTTPException(status_code=403, detail="Chat allowed only with matches")

    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    db.save_message(user_id, other_user_id, message)
    db.update_message_stats(user_id, other_user_id)
    return {"ok": True}


@app.post("/api/gifts/send")
def send_gift(request: SendGiftRequest, claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    if not db.is_match(user_id, request.to_user_id):
        raise HTTPException(status_code=403, detail="Gifts allowed only with matches")

    gift_name = GIFT_CATALOG.get(request.gift_code)
    if not gift_name:
        raise HTTPException(status_code=400, detail="Unknown gift")

    db.send_gift(user_id, request.to_user_id, request.gift_code, gift_name, request.gift_message)
    return {"ok": True}


@app.get("/api/gifts/received")
def get_received_gifts(claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, Any]:
    user_id = int(claims["uid"])
    gifts = db.get_received_gifts(user_id, limit=50)
    return {"gifts": gifts}


@app.get("/api/share-link")
def get_share_link(claims: Dict[str, Any] = Depends(_get_claims)) -> Dict[str, str]:
    user_id = int(claims["uid"])
    username = (BOT_USERNAME or "").strip().replace("@", "")
    if not username:
        return {
            "share_url": "https://t.me/share/url?url=https://t.me&text=Join%20our%20dating%20bot"
        }

    bot_link = f"https://t.me/{username}?start=ref_{user_id}"
    return {
        "share_url": f"https://t.me/share/url?url={bot_link}&text=Join%20me%20in%20this%20dating%20bot"
    }
