from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from .. import constants
from ..config import Settings
from ..keyboards import main_menu_keyboard, registration_success_keyboard, voting_card_keyboard
from ..storage import Store
from ..utils.gate import is_channel_member

log = logging.getLogger(__name__)


def _is_owner(update: Update, settings: Settings) -> bool:
    return update.effective_user is not None and update.effective_user.id == settings.owner_id


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]

    # Participant deep-link: /start join_<code>
    if context.args and context.args[0].startswith("join_"):
        await _handle_join(update, context, context.args[0].removeprefix("join_"))
        return

    if _is_owner(update, settings):
        channel = await store.get_channel()
        await update.message.reply_text(
            constants.welcome_panel(channel_connected=channel is not None),
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard(),
        )
    else:
        await update.message.reply_text(
            f'{constants.pe("clover")} <b>{constants.BOT_NAME}</b> — lucky-draw giveaways.\n'
            f'Join links are shared in the channel once a giveaway is live.',
            parse_mode=ParseMode.HTML,
        )


async def _handle_join(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str) -> None:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    user = update.effective_user

    giveaway = await store.get_by_code(code)
    if giveaway is None or giveaway["status"] != "active":
        await update.message.reply_text(constants.join_no_giveaway(), parse_mode=ParseMode.HTML)
        return

    channel = await store.get_channel()
    channel_id = giveaway["channel_id"]
    channel_link = channel.get("channel_link") if channel else None

    if not await is_channel_member(context.bot, channel_id, user.id):
        gate_text = constants.join_needs_gate(channel_link or "")
        await update.message.reply_text(gate_text, parse_mode=ParseMode.HTML)
        return

    existing = await store.get_participant(giveaway["_id"], user.id)
    if existing:
        await update.message.reply_text(constants.join_already_joined(), parse_mode=ParseMode.HTML)
        return

    participant, is_new = await store.upsert_participant(
        giveaway["_id"], user.id, user.username, user.full_name
    )

    # Post their own shareable voting card to the channel.
    try:
        card_text = constants.voting_card(
            participant["full_name"], participant["user_id"], participant["votes"]
        )
        card_keyboard = voting_card_keyboard(str(participant["_id"]), participant["votes"])
        sent = await context.bot.send_message(
            chat_id=channel_id, text=card_text, parse_mode=ParseMode.HTML, reply_markup=card_keyboard
        )
        await store.set_card_message_id(participant["_id"], sent.message_id)
        await store.increment_participant_count(giveaway["_id"])
    except Exception:
        log.exception("Failed to post voting card for participant %s", user.id)
        await update.message.reply_text(
            f'{constants.pe("card")} Joined, but couldn\'t post your card — contact the owner.',
            parse_mode=ParseMode.HTML,
        )
        return

    share_link = f"https://t.me/{settings.bot_username}?start=join_{giveaway['code']}"
    await update.message.reply_text(
        constants.registration_success(share_link),
        parse_mode=ParseMode.HTML,
        reply_markup=registration_success_keyboard(),
    )