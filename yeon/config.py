from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _require_int(name: str) -> int:
    raw = os.getenv(name)
    if not raw:
        raise RuntimeError(f"Missing required env var: {name}")
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer, got: {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    bot_token: str
    bot_username: str
    owner_id: int
    logger_group_id: int
    qr_image: str
    mongo_uri: str
    mongo_db_name: str
    rupees_per_vote: float
    stars_per_vote: float


def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("Missing required env var: BOT_TOKEN")

    bot_username = os.getenv("BOT_USERNAME")
    if not bot_username:
        raise RuntimeError("Missing required env var: BOT_USERNAME (without @)")

    return Settings(
        bot_token=bot_token,
        bot_username=bot_username.lstrip("@"),
        owner_id=_require_int("OWNER_ID"),
        logger_group_id=_require_int("LOGGER_GROUP_ID"),
        qr_image=os.getenv("QR_IMAGE", "assets/qr.jpg"),
        mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        mongo_db_name=os.getenv("MONGO_DB_NAME", "yeondb"),
        rupees_per_vote=float(os.getenv("RUPEES_PER_VOTE", "0.5")),
        stars_per_vote=float(os.getenv("STARS_PER_VOTE", "2")),
    )
