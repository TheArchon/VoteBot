from __future__ import annotations

import logging
import secrets
import string as _string

from bson import ObjectId
from bson.errors import InvalidId
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes, ConversationHandler

from .. import constants
from ..config import Settings
from ..keyboards import (
    back_to_manage_keyboard,
    cancel_keyboard,
    end_confirm_keyboard,
    giveaway_created_keyboard,
    join_giveaway_keyboard,
    main_menu_keyboard,
    management_panel_keyboard,
    voting_card_keyboard,
)
from ..storage import Store
from ..utils.gate import is_channel_member
from .anticheat import evaluate_vote_risk

log = logging.getLogger(__name__)

AWAITING_CHANNEL, AWAITING_PRIZE, AWAITING_VOTE_ADJUST = range(3)


def _is_owner(update: Update, settings: Settings) -> bool:
    user = update.effective_user
    return user is not None and user.id == settings.owner_id


def _actor_label(update: Update) -> str:
    user = update.effective_user
    return f"@{user.username}" if user and user.username else str(user.id if user else "unknown")


async def _edit_or_reply(update: Update, text: str, reply_markup=None) -> None:
    query = update.callback_query
    if query:
        await query.answer()
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        except TelegramError:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


# ------------------------------------------------------------------- home

async def go_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    if not _is_owner(update, settings):
        return ConversationHandler.END

    channel = await store.get_channel()
    await _edit_or_reply(
        update, constants.welcome_panel(channel_connected=channel is not None), main_menu_keyboard()
    )
    return ConversationHandler.END


async def cancel_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await go_home(update, context)


# ---------------------------------------------------------------- connect

async def connect_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    if not _is_owner(update, settings):
        return ConversationHandler.END
    await _edit_or_reply(update, constants.connect_prompt(), cancel_keyboard())
    return AWAITING_CHANNEL


async def connect_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    store: Store = context.bot_data["store"]
    raw = update.message.text.strip()

    try:
        chat = await context.bot.get_chat(raw)
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
        if bot_member.status not in ("administrator", "creator"):
            raise TelegramError("bot is not an admin there")
    except TelegramError:
        await update.message.reply_text(constants.connect_failed(), parse_mode=ParseMode.HTML)
        return AWAITING_CHANNEL

    if chat.username:
        link = f"https://t.me/{chat.username}"
    else:
        try:
            link = await context.bot.export_chat_invite_link(chat.id)
        except TelegramError:
            link = ""

    channel_title = chat.title or chat.username or str(chat.id)
    await store.set_channel(chat.id, channel_title, link)

    await update.message.reply_text(
        constants.connect_success(channel_title), parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


# ----------------------------------------------------------------- create

async def create_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    if not _is_owner(update, settings):
        return ConversationHandler.END

    channel = await store.get_channel()
    if channel is None:
        await _edit_or_reply(update, constants.create_no_channel(), main_menu_keyboard())
        return ConversationHandler.END

    if await store.get_active_giveaway():
        await _edit_or_reply(
            update,
            f'{constants.pe("card")} There\'s already an active giveaway. '
            f"End it first from MANAGE.",
            main_menu_keyboard(),
        )
        return ConversationHandler.END

    await _edit_or_reply(update, constants.create_prize_prompt(), cancel_keyboard())
    return AWAITING_PRIZE


async def create_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    channel = await store.get_channel()
    if channel is None:
        await update.message.reply_text(constants.create_no_channel(), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    skip = bool(update.message.text) and update.message.text.strip().upper() == "SKIP"

    code = "".join(secrets.choice(_string.ascii_uppercase + _string.digits) for _ in range(6))
    while await store.get_by_code(code):
        code = "".join(secrets.choice(_string.ascii_uppercase + _string.digits) for _ in range(6))

    keyboard = join_giveaway_keyboard(settings.bot_username, code)

    try:
        if skip:
            sent = await context.bot.send_message(
                chat_id=channel["channel_id"],
                text=constants.default_giveaway_announcement(),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        else:
            sent = await context.bot.copy_message(
                chat_id=channel["channel_id"],
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
                reply_markup=keyboard,
            )
    except TelegramError:
        log.exception("Failed to publish giveaway announcement.")
        await update.message.reply_text(constants.create_post_failed(), parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    giveaway = await store.create_giveaway(channel["channel_id"], sent.message_id, code=code)

    link = f"https://t.me/{settings.bot_username}?start=join_{giveaway['code']}"
    await update.message.reply_text(
        constants.giveaway_created(giveaway["code"], channel["channel_title"], link),
        parse_mode=ParseMode.HTML,
        reply_markup=giveaway_created_keyboard(),
    )

    try:
        await context.bot.send_message(
            chat_id=settings.logger_group_id,
            text=constants.logger_giveaway_created(_actor_label(update), channel["channel_title"]),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass

    return ConversationHandler.END


# ---------------------------------------------------------------- manage

async def show_manage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    if not _is_owner(update, settings):
        return

    channel = await store.get_channel()
    if channel is None:
        await _edit_or_reply(update, constants.manage_no_channel(), main_menu_keyboard())
        return

    giveaway = await store.get_active_giveaway()
    if giveaway is None:
        await _edit_or_reply(update, constants.manage_no_giveaway(), main_menu_keyboard())
        return

    await _edit_or_reply(
        update,
        constants.management_panel(giveaway["status"], channel["channel_title"], giveaway["participant_count"]),
        management_panel_keyboard(),
    )


async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    store: Store = context.bot_data["store"]
    giveaway = await store.get_active_giveaway()
    if giveaway is None:
        await _edit_or_reply(update, constants.manage_no_giveaway(), main_menu_keyboard())
        return

    entries = await store.leaderboard(giveaway["_id"])
    if not entries:
        text = constants.leaderboard_empty()
    else:
        labeled = [
            (f"@{e['username']}" if e.get("username") else e["full_name"], e["votes"]) for e in entries
        ]
        text = constants.leaderboard(labeled)
    await _edit_or_reply(update, text, back_to_manage_keyboard())


async def end_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    if not _is_owner(update, settings):
        return
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f'{constants.pe("card")} Are you sure you want to end this giveaway?',
        parse_mode=ParseMode.HTML,
        reply_markup=end_confirm_keyboard(),
    )


async def end_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    if not _is_owner(update, settings):
        return
    query = update.callback_query
    await query.answer()

    giveaway = await store.get_active_giveaway()
    if giveaway is None:
        await query.edit_message_text(
            constants.manage_no_giveaway(), parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard()
        )
        return

    await store.end_giveaway(giveaway["_id"])
    top = await store.top_participant(giveaway["_id"])
    winner_label = None
    if top:
        winner_label = f"@{top['username']}" if top.get("username") else top["full_name"]

    result_text = constants.giveaway_ended(winner_label)
    await query.edit_message_text(result_text, parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard())

    try:
        await context.bot.send_message(
            chat_id=giveaway["channel_id"], text=result_text, parse_mode=ParseMode.HTML
        )
    except Exception:
        pass
    try:
        await context.bot.send_message(
            chat_id=settings.logger_group_id,
            text=constants.logger_giveaway_ended(_actor_label(update)),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass


# ----------------------------------------------------------- add/remove votes

async def addvotes_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    if not _is_owner(update, settings):
        return ConversationHandler.END
    context.user_data["vote_mode"] = "add"
    await _edit_or_reply(update, constants.add_votes_prompt(), back_to_manage_keyboard())
    return AWAITING_VOTE_ADJUST


async def removevotes_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    if not _is_owner(update, settings):
        return ConversationHandler.END
    context.user_data["vote_mode"] = "remove"
    await _edit_or_reply(update, constants.remove_votes_prompt(), back_to_manage_keyboard())
    return AWAITING_VOTE_ADJUST


async def vote_adjust_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    store: Store = context.bot_data["store"]
    parts = update.message.text.strip().split()

    if len(parts) != 2 or not all(p.lstrip("-").isdigit() for p in parts):
        await update.message.reply_text(constants.vote_adjust_bad_format(), parse_mode=ParseMode.HTML)
        return AWAITING_VOTE_ADJUST

    target_user_id, amount = int(parts[0]), abs(int(parts[1]))
    mode = context.user_data.get("vote_mode", "add")

    giveaway = await store.get_active_giveaway()
    if giveaway is None:
        await update.message.reply_text(
            constants.manage_no_giveaway(), parse_mode=ParseMode.HTML, reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    delta = amount if mode == "add" else -amount
    new_total = await store.adjust_votes(giveaway["_id"], target_user_id, delta, label_fallback=str(target_user_id))

    text = (
        constants.votes_added(target_user_id, amount, new_total)
        if mode == "add"
        else constants.votes_removed(target_user_id, amount, new_total)
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=back_to_manage_keyboard())

    participant = await store.get_participant(giveaway["_id"], target_user_id)
    if participant and participant.get("card_message_id"):
        try:
            await context.bot.edit_message_text(
                chat_id=giveaway["channel_id"],
                message_id=participant["card_message_id"],
                text=constants.voting_card(participant["full_name"], participant["user_id"], new_total),
                parse_mode=ParseMode.HTML,
                reply_markup=voting_card_keyboard(str(participant["_id"]), new_total),
            )
        except TelegramError:
            pass

    return ConversationHandler.END


# ------------------------------------------------------------------- voting

async def vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    query = update.callback_query
    raw_id = query.data.removeprefix("vote_")

    try:
        participant_id = ObjectId(raw_id)
    except InvalidId:
        await query.answer(constants.vote_gone(), show_alert=True)
        return

    participant = await store.get_participant_by_id(participant_id)
    if participant is None:
        await query.answer(constants.vote_gone(), show_alert=True)
        return

    giveaway = await store.giveaways.find_one({"_id": participant["giveaway_id"]})
    if giveaway is None or giveaway["status"] != "active":
        await query.answer(constants.vote_gone(), show_alert=True)
        return

    voter = query.from_user
    voter_id = voter.id
    if voter_id == participant["user_id"]:
        await query.answer("You can't vote for yourself!", show_alert=True)
        return

    if not await is_channel_member(context.bot, giveaway["channel_id"], voter_id):
        await query.answer(constants.vote_needs_gate(), show_alert=True)
        return

    # --- Anti-cheat: block automated/bulk/SMM-panel-style votes ---
    risk_reasons = await evaluate_vote_risk(
        context.bot, store, giveaway["channel_id"], participant_id, voter
    )
    if risk_reasons:
        await store.log_vote_event(
            giveaway["_id"], participant_id, voter_id, blocked=True, reasons=risk_reasons
        )
        await query.answer(constants.vote_blocked_suspicious(), show_alert=True)

        try:
            await context.bot.send_message(
                chat_id=voter_id,
                text=constants.anticheat_voter_warning(),
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass  # voter may have blocked the bot — nothing more we can do

        try:
            blocked_total = await store.count_blocked_votes(participant_id)
            await context.bot.send_message(
                chat_id=settings.logger_group_id,
                text=constants.anticheat_owner_report(
                    participant["full_name"], voter_id, risk_reasons, blocked_total
                ),
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            log.exception("Failed to send anti-cheat report to logger group.")
        return

    status, new_total = await store.cast_vote(participant_id, voter_id)
    if status == "already_voted":
        await query.answer(constants.vote_already_voted(), show_alert=True)
        return
    if status == "not_found":
        await query.answer(constants.vote_gone(), show_alert=True)
        return

    await store.log_vote_event(giveaway["_id"], participant_id, voter_id, blocked=False, reasons=[])

    await query.answer(constants.vote_recorded())
    try:
        await query.edit_message_text(
            constants.voting_card(participant["full_name"], participant["user_id"], new_total),
            parse_mode=ParseMode.HTML,
            reply_markup=voting_card_keyboard(raw_id, new_total),
        )
    except TelegramError:
        pass