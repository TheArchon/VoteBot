"""
MongoDB-backed persistence for Yeon.

Database: yeondb (configurable via MONGO_DB_NAME)

Collections:
  channel_config — singleton doc: the currently connected channel
  giveaways      — one giveaway per doc; only one 'active' at a time
  participants   — per (giveaway, user) vote records
  vote_purchases — cash/stars vote purchase records
  channel_joins  — most-recent join timestamp per (channel, user); used by
                   anti-cheat to flag "joined seconds ago, voted instantly"
  vote_events    — a log of every vote attempt (allowed or blocked); used
                   by anti-cheat to detect vote-velocity spikes and to
                   report suspicious activity to the owner
"""
from __future__ import annotations

import random
import string
from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _gen_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphabet, k=length))


class Store:
    def __init__(self, mongo_uri: str, db_name: str = "yeondb"):
        self._client = AsyncIOMotorClient(mongo_uri)
        self._db = self._client[db_name]
        self.channel_config = self._db["channel_config"]
        self.giveaways = self._db["giveaways"]
        self.participants = self._db["participants"]
        self.vote_purchases = self._db["vote_purchases"]
        self.channel_joins = self._db["channel_joins"]
        self.vote_events = self._db["vote_events"]

    # -------------------------------------------------------- channel config

    async def set_channel(self, channel_id: int, channel_title: str, channel_link: str) -> None:
        await self.channel_config.update_one(
            {"_id": "singleton"},
            {
                "$set": {
                    "channel_id": channel_id,
                    "channel_title": channel_title,
                    "channel_link": channel_link,
                    "connected_at": _now(),
                }
            },
            upsert=True,
        )

    async def get_channel(self) -> dict | None:
        return await self.channel_config.find_one({"_id": "singleton"})

    # ------------------------------------------------------------ giveaways

    async def get_active_giveaway(self) -> dict | None:
        return await self.giveaways.find_one({"status": "active"})

    async def create_giveaway(self, channel_id: int, announcement_message_id: int, code: str | None = None) -> dict:
        if code is None:
            code = _gen_code()
        while await self.giveaways.find_one({"code": code}):
            code = _gen_code()

        doc = {
            "code": code,
            "channel_id": channel_id,
            "status": "active",
            "announcement_message_id": announcement_message_id,
            "participant_count": 0,
            "created_at": _now(),
            "ended_at": None,
        }
        result = await self.giveaways.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def get_by_code(self, code: str) -> dict | None:
        return await self.giveaways.find_one({"code": code.strip().upper()})

    async def increment_participant_count(self, giveaway_id) -> int:
        result = await self.giveaways.find_one_and_update(
            {"_id": giveaway_id},
            {"$inc": {"participant_count": 1}},
            return_document=ReturnDocument.AFTER,
        )
        return result["participant_count"] if result else 0

    async def end_giveaway(self, giveaway_id) -> None:
        await self.giveaways.update_one(
            {"_id": giveaway_id}, {"$set": {"status": "ended", "ended_at": _now()}}
        )

    # ---------------------------------------------------------- participants

    async def get_participant(self, giveaway_id, user_id: int) -> dict | None:
        return await self.participants.find_one({"giveaway_id": giveaway_id, "user_id": user_id})

    async def upsert_participant(
        self, giveaway_id, user_id: int, username: str | None, full_name: str
    ) -> tuple[dict, bool]:
        """Returns (participant, is_new)."""
        existing = await self.get_participant(giveaway_id, user_id)
        if existing:
            return existing, False

        doc = {
            "giveaway_id": giveaway_id,
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "votes": 0,
            "voters": [],  # user_ids who have voted for this participant (prevents duplicate votes)
            "card_message_id": None,
            "joined_at": _now(),
        }
        result = await self.participants.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc, True

    async def set_card_message_id(self, participant_id, message_id: int) -> None:
        await self.participants.update_one(
            {"_id": participant_id}, {"$set": {"card_message_id": message_id}}
        )

    async def cast_vote(self, participant_id, voter_user_id: int) -> tuple[str, int]:
        """
        Atomically records a vote from voter_user_id for the given
        participant. Returns (status, new_vote_count):
          status = "ok"              — vote recorded
          status = "already_voted"   — this voter already voted for them
          status = "not_found"       — participant no longer exists
        """
        participant = await self.participants.find_one({"_id": participant_id})
        if participant is None:
            return "not_found", 0
        if voter_user_id in participant.get("voters", []):
            return "already_voted", participant["votes"]

        result = await self.participants.find_one_and_update(
            {"_id": participant_id, "voters": {"$ne": voter_user_id}},
            {"$inc": {"votes": 1}, "$push": {"voters": voter_user_id}},
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            # Lost a race — someone else's concurrent update got there first
            # and voter_user_id is now present; treat as already-voted.
            return "already_voted", participant["votes"]
        return "ok", result["votes"]

    async def get_participant_by_id(self, participant_id) -> dict | None:
        return await self.participants.find_one({"_id": participant_id})

    async def find_participants_voted_by(self, giveaway_id, voter_user_id: int) -> list[dict]:
        """All participants this voter has an active vote on, in this giveaway."""
        cursor = self.participants.find({"giveaway_id": giveaway_id, "voters": voter_user_id})
        return [doc async for doc in cursor]

    async def revoke_vote(self, participant_id, voter_user_id: int) -> int:
        """Removes one vote cast by voter_user_id (anti-cheat: they left the
        channel). Returns the new vote total (never below 0)."""
        result = await self.participants.find_one_and_update(
            {"_id": participant_id, "voters": voter_user_id},
            {"$inc": {"votes": -1}, "$pull": {"voters": voter_user_id}},
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            current = await self.participants.find_one({"_id": participant_id})
            return current["votes"] if current else 0
        if result["votes"] < 0:
            result = await self.participants.find_one_and_update(
                {"_id": participant_id}, {"$set": {"votes": 0}}, return_document=ReturnDocument.AFTER
            )
        return result["votes"]

    # ------------------------------------------------------------ purchases

    async def create_purchase(
        self, giveaway_id, participant_id, user_id: int, votes: int, method: str
    ) -> dict:
        doc = {
            "giveaway_id": giveaway_id,
            "participant_id": participant_id,
            "user_id": user_id,
            "votes": votes,
            "method": method,  # "cash" | "stars"
            "status": "pending",
            "screenshot_file_id": None,
            "created_at": _now(),
            "reviewed_at": None,
        }
        result = await self.vote_purchases.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def set_purchase_screenshot(self, purchase_id, file_id: str) -> None:
        await self.vote_purchases.update_one(
            {"_id": purchase_id}, {"$set": {"screenshot_file_id": file_id}}
        )

    async def get_purchase(self, purchase_id) -> dict | None:
        return await self.vote_purchases.find_one({"_id": purchase_id})

    async def set_purchase_status(self, purchase_id, status: str) -> None:
        await self.vote_purchases.update_one(
            {"_id": purchase_id}, {"$set": {"status": status, "reviewed_at": _now()}}
        )

    async def adjust_votes(self, giveaway_id, user_id: int, delta: int, label_fallback: str) -> int:
        """
        Adds delta (can be negative) to a participant's vote count. Creates
        the participant record if it doesn't exist yet (manual owner
        override — doesn't require the user to have joined via the bot).
        Returns the new vote total (never below 0).
        """
        existing = await self.get_participant(giveaway_id, user_id)
        if existing is None:
            await self.participants.insert_one(
                {
                    "giveaway_id": giveaway_id,
                    "user_id": user_id,
                    "username": None,
                    "full_name": label_fallback,
                    "votes": 0,
                    "voters": [],
                    "card_message_id": None,
                    "joined_at": _now(),
                }
            )

        result = await self.participants.find_one_and_update(
            {"giveaway_id": giveaway_id, "user_id": user_id},
            {"$inc": {"votes": delta}},
            return_document=ReturnDocument.AFTER,
        )
        if result["votes"] < 0:
            result = await self.participants.find_one_and_update(
                {"giveaway_id": giveaway_id, "user_id": user_id},
                {"$set": {"votes": 0}},
                return_document=ReturnDocument.AFTER,
            )
        return result["votes"]

    async def leaderboard(self, giveaway_id, limit: int = 10) -> list[dict]:
        cursor = self.participants.find({"giveaway_id": giveaway_id}).sort("votes", -1).limit(limit)
        return [doc async for doc in cursor]

    async def top_participant(self, giveaway_id) -> dict | None:
        top = await self.leaderboard(giveaway_id, limit=1)
        return top[0] if top else None

    # ------------------------------------------------------------ anti-cheat

    async def record_channel_join(self, channel_id: int, user_id: int) -> None:
        """Timestamps the most recent moment this user joined the channel.
        Used to flag 'joined seconds ago, voted immediately' bot-like
        behavior typical of SMM-panel / bulk-account abuse."""
        await self.channel_joins.update_one(
            {"channel_id": channel_id, "user_id": user_id},
            {"$set": {"joined_at": _now()}},
            upsert=True,
        )

    async def get_channel_join_time(self, channel_id: int, user_id: int) -> datetime | None:
        doc = await self.channel_joins.find_one({"channel_id": channel_id, "user_id": user_id})
        return doc["joined_at"] if doc else None

    async def log_vote_event(
        self, giveaway_id, participant_id, voter_id: int, blocked: bool, reasons: list[str]
    ) -> None:
        """Logs every vote attempt (allowed or blocked). Powers the
        vote-velocity check and the owner's suspicious-activity report."""
        await self.vote_events.insert_one(
            {
                "giveaway_id": giveaway_id,
                "participant_id": participant_id,
                "voter_id": voter_id,
                "blocked": blocked,
                "reasons": reasons,
                "timestamp": _now(),
            }
        )

    async def count_recent_votes(self, participant_id, window_seconds: int) -> int:
        """Counts this participant's *allowed* votes in the last window —
        used to detect a sudden burst (vote-velocity spike)."""
        since = _now() - timedelta(seconds=window_seconds)
        return await self.vote_events.count_documents(
            {"participant_id": participant_id, "blocked": False, "timestamp": {"$gte": since}}
        )

    async def count_blocked_votes(self, participant_id) -> int:
        """Total suspicious/blocked vote attempts for this participant in
        this giveaway — included in the owner's report so they can judge
        severity (one-off vs. repeated abuse)."""
        return await self.vote_events.count_documents({"participant_id": participant_id, "blocked": True})

    async def close(self) -> None:
        self._client.close()