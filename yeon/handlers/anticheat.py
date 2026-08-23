from __future__ import annotations

import logging
from datetime import datetime, timezone

from telegram import Update, User
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from .. import constants
from ..keyboards import voting_card_keyboard
from ..storage import Store

log = logging.getLogger(__name__)

_MEMBER_STATUSES = {"member", "administrator", "creator"}

# --- Anti-cheat thresholds ---------------------------------------------
# Joined the channel less than this long ago and already voting —
# classic SMM-panel / freshly-created-bulk-account behavior.
JOIN_GRACE_SECONDS = 5 * 60

# If a participant receives this many (or more) allowed votes within the
# window below, the newest vote is treated as a velocity spike.
VELOCITY_WINDOW_SECONDS = 3 * 60
VELOCITY_THRESHOLD = 8

_REASON_LABELS = {
    "joined_recently": "Joined the channel less than 5 minutes before voting",
    "no_username_no_photo": "No username and no profile photo (typical bulk/bot account)",
    "velocity_spike": "Sudden burst of votes for this participant in a short window",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _delete_message_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data
    try:
        await context.bot.delete_message(chat_id=data["chat_id"], message_id=data["message_id"])
    except TelegramError:
        pass


async def _has_no_profile_photo(bot, user_id: int) -> bool:
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        return photos.total_count == 0
    except TelegramError:
        # Fail open — an API hiccup shouldn't get an innocent voter blocked.
        return False


async def evaluate_vote_risk(
    bot, store: Store, channel_id: int, participant_id, voter: User
) -> list[str]:
    """
    Runs all anti-cheat heuristics for one vote attempt. Returns a list of
    reason codes — empty list means the vote looks clean.
    """
    reasons: list[str] = []

    join_time = await store.get_channel_join_time(channel_id, voter.id)
    if join_time is not None:
        age_seconds = (_now() - join_time).total_seconds()
        if age_seconds < JOIN_GRACE_SECONDS:
            reasons.append("joined_recently")

    if not voter.username and await _has_no_profile_photo(bot, voter.id):
        reasons.append("no_username_no_photo")

    recent_votes = await store.count_recent_votes(participant_id, VELOCITY_WINDOW_SECONDS)
    if recent_votes >= VELOCITY_THRESHOLD:
        reasons.append("velocity_spike")

    return reasons


def reason_summary(reasons: list[str]) -> str:
    return "\n".join(f"• {_REASON_LABELS.get(r, r)}" for r in reasons)


async def handle_channel_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Fires on every membership change in any chat the bot administers.
    We only care about the connected giveaway channel:

    - Someone JOINING → timestamp it (used by evaluate_vote_risk to flag
      join-then-vote bursts).
    - Someone LEAVING → revoke any votes they cast (existing behavior).
    """
    store: Store = context.bot_data["store"]
    cmu = update.chat_member

    channel = await store.get_channel()
    if channel is None or cmu.chat.id != channel["channel_id"]:
        return

    was_member = cmu.old_chat_member.status in _MEMBER_STATUSES
    is_member = cmu.new_chat_member.status in _MEMBER_STATUSES

    if not was_member and is_member:
        await store.record_channel_join(channel["channel_id"], cmu.new_chat_member.user.id)
        return

    if not (was_member and not is_member):
        return  # not a "left the channel" transition

    leaver = cmu.new_chat_member.user
    giveaway = await store.get_active_giveaway()
    if giveaway is None:
        return

    affected = await store.find_participants_voted_by(giveaway["_id"], leaver.id)
    for participant in affected:
        new_total = await store.revoke_vote(participant["_id"], leaver.id)

        if participant.get("card_message_id"):
            try:
                await context.bot.edit_message_text(
                    chat_id=channel["channel_id"],
                    message_id=participant["card_message_id"],
                    text=constants.voting_card(participant["full_name"], participant["user_id"], new_total),
                    parse_mode=ParseMode.HTML,
                    reply_markup=voting_card_keyboard(str(participant["_id"]), new_total),
                )
            except TelegramError:
                pass

        try:
            notice = await context.bot.send_message(
                chat_id=channel["channel_id"],
                text=constants.vote_revoked_notice(participant["full_name"], new_total),
                parse_mode=ParseMode.HTML,
            )
            if context.job_queue:
                context.job_queue.run_once(
                    _delete_message_job,
                    when=60,
                    data={"chat_id": channel["channel_id"], "message_id": notice.message_id},
                )
        except TelegramError:
            log.exception("Failed to post vote-revoked notice.")