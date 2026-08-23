from __future__ import annotations

from telegram import Bot
from telegram.error import TelegramError

_MEMBER_STATUSES = {"member", "administrator", "creator"}


async def is_channel_member(bot: Bot, channel_id: int, user_id: int) -> bool:
    """
    Checks whether user_id is currently a member of channel_id.
    Requires the bot to be an admin of that channel. Fails closed (returns
    False) on any lookup error, so membership gates stay up by default.
    """
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
    except TelegramError:
        return False
    return member.status in _MEMBER_STATUSES
