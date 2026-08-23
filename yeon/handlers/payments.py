from __future__ import annotations

import logging

from bson import ObjectId
from bson.errors import InvalidId
from telegram import InputFile, LabeledPrice, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes, ConversationHandler

from .. import constants
from ..config import Settings
from ..keyboards import purchase_review_keyboard, voting_card_keyboard
from ..storage import Store

log = logging.getLogger(__name__)

ASK_QTY_CASH, ASK_QTY_STARS, ASK_SCREENSHOT = range(20, 23)


async def _get_buyer_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resolves the active giveaway + this user's participant record, if any."""
    store: Store = context.bot_data["store"]
    giveaway = await store.get_active_giveaway()
    if giveaway is None:
        return None, None
    participant = await store.get_participant(giveaway["_id"], update.effective_user.id)
    return giveaway, participant


# ------------------------------------------------------------------- cash

async def buyvotes_cash_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    giveaway, participant = await _get_buyer_context(update, context)
    if giveaway is None or participant is None:
        await query.answer("Join a giveaway first!", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    context.user_data["buy_giveaway_id"] = giveaway["_id"]
    context.user_data["buy_participant_id"] = participant["_id"]
    await query.message.reply_text(constants.buy_qty_prompt("cash"), parse_mode=ParseMode.HTML)
    return ASK_QTY_CASH


async def receive_qty_cash(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await update.message.reply_text(constants.buy_qty_invalid(), parse_mode=ParseMode.HTML)
        return ASK_QTY_CASH

    votes = int(text)
    rupees = votes * settings.rupees_per_vote
    context.user_data["buy_votes_qty"] = votes

    try:
        with open(settings.qr_image, "rb") as qr:
            await update.message.reply_photo(
                photo=InputFile(qr),
                caption=constants.buy_cash_qr_caption(votes, rupees),
                parse_mode=ParseMode.HTML,
            )
    except FileNotFoundError:
        log.warning("QR image not found at %s — sending text only.", settings.qr_image)
        await update.message.reply_text(
            constants.buy_cash_qr_caption(votes, rupees), parse_mode=ParseMode.HTML
        )

    return ASK_SCREENSHOT


async def receive_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]

    if not update.message.photo:
        await update.message.reply_text(constants.buy_cash_awaiting_screenshot(), parse_mode=ParseMode.HTML)
        return ASK_SCREENSHOT

    giveaway_id = context.user_data.get("buy_giveaway_id")
    participant_id = context.user_data.get("buy_participant_id")
    votes = context.user_data.get("buy_votes_qty")
    if not all([giveaway_id, participant_id, votes]):
        await update.message.reply_text(
            f'{constants.pe("card")} Something went wrong — please start again from your voting card DM.',
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    purchase = await store.create_purchase(
        giveaway_id, participant_id, update.effective_user.id, votes, method="cash"
    )
    file_id = update.message.photo[-1].file_id
    await store.set_purchase_screenshot(purchase["_id"], file_id)

    user = update.effective_user
    buyer_label = f"@{user.username}" if user.username else user.full_name
    rupees = votes * settings.rupees_per_vote

    try:
        await context.bot.send_photo(
            chat_id=settings.logger_group_id,
            photo=file_id,
            caption=constants.logger_purchase_review(buyer_label, votes, rupees),
            parse_mode=ParseMode.HTML,
            reply_markup=purchase_review_keyboard(str(purchase["_id"])),
        )
    except TelegramError:
        log.exception("Failed to forward purchase screenshot to logger group.")

    await update.message.reply_text(constants.buy_cash_submitted(), parse_mode=ParseMode.HTML)
    return ConversationHandler.END


# ----------------------------------------------------------- owner review

def _is_owner(update: Update, settings: Settings) -> bool:
    user = update.effective_user
    return user is not None and user.id == settings.owner_id


async def purchase_accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    if not _is_owner(update, settings):
        return
    query = update.callback_query
    await query.answer()

    purchase_id_str = query.data.removeprefix("purchase_accept_")
    try:
        purchase = await store.get_purchase(ObjectId(purchase_id_str))
    except InvalidId:
        purchase = None
    if purchase is None or purchase["status"] != "pending":
        await query.answer("Already handled.", show_alert=True)
        return

    giveaway = await store.giveaways.find_one({"_id": purchase["giveaway_id"]})
    participant = await store.get_participant_by_id(purchase["participant_id"])
    buyer_id = purchase["user_id"]

    try:
        buyer = await context.bot.get_chat(buyer_id)
        buyer_label = f"@{buyer.username}" if buyer.username else str(buyer_id)
    except TelegramError:
        buyer_label = str(buyer_id)

    if giveaway is None or participant is None:
        await store.set_purchase_status(purchase["_id"], "accepted")
        await query.answer("Giveaway/participant record not found — credit manually.", show_alert=True)
        return

    # Credit the votes immediately — we already know exactly which
    # participant this purchase belongs to, no need to ask for a link.
    new_total = await store.adjust_votes(
        giveaway["_id"], buyer_id, purchase["votes"], label_fallback=participant["full_name"]
    )
    await store.set_purchase_status(purchase["_id"], "completed")

    if participant.get("card_message_id"):
        try:
            await context.bot.edit_message_text(
                chat_id=giveaway["channel_id"],
                message_id=participant["card_message_id"],
                text=constants.voting_card(participant["full_name"],participant["user_id"], new_total),
                parse_mode=ParseMode.HTML,
                reply_markup=voting_card_keyboard(str(participant["_id"]), new_total),
            )
        except TelegramError:
            pass

    try:
        await context.bot.send_message(
            chat_id=buyer_id,
            text=constants.purchase_votes_credited(purchase["votes"], new_total),
            parse_mode=ParseMode.HTML,
        )
    except TelegramError:
        log.exception("Failed to DM buyer after crediting votes.")

    try:
        await query.edit_message_caption(
            caption=constants.purchase_review_resolved_accept(buyer_label), parse_mode=ParseMode.HTML
        )
    except TelegramError:
        pass


async def purchase_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    store: Store = context.bot_data["store"]
    if not _is_owner(update, settings):
        return
    query = update.callback_query
    await query.answer()

    purchase_id_str = query.data.removeprefix("purchase_reject_")
    try:
        purchase = await store.get_purchase(ObjectId(purchase_id_str))
    except InvalidId:
        purchase = None
    if purchase is None or purchase["status"] != "pending":
        await query.answer("Already handled.", show_alert=True)
        return

    await store.set_purchase_status(purchase["_id"], "rejected")

    buyer_id = purchase["user_id"]
    try:
        buyer = await context.bot.get_chat(buyer_id)
        buyer_label = f"@{buyer.username}" if buyer.username else str(buyer_id)
    except TelegramError:
        buyer_label = str(buyer_id)

    try:
        await context.bot.send_message(
            chat_id=buyer_id, text=constants.purchase_rejected(), parse_mode=ParseMode.HTML
        )
    except TelegramError:
        pass

    try:
        await query.edit_message_caption(
            caption=constants.purchase_review_resolved_reject(buyer_label), parse_mode=ParseMode.HTML
        )
    except TelegramError:
        pass


# ------------------------------------------------------------------ stars

async def buyvotes_stars_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    giveaway, participant = await _get_buyer_context(update, context)
    if giveaway is None or participant is None:
        await query.answer("Join a giveaway first!", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    context.user_data["buy_giveaway_id"] = giveaway["_id"]
    context.user_data["buy_participant_id"] = participant["_id"]
    await query.message.reply_text(constants.buy_qty_prompt("stars"), parse_mode=ParseMode.HTML)
    return ASK_QTY_STARS


async def receive_qty_stars(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    text = update.message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await update.message.reply_text(constants.buy_qty_invalid(), parse_mode=ParseMode.HTML)
        return ASK_QTY_STARS

    votes = int(text)
    stars_amount = max(1, round(votes * settings.stars_per_vote))
    giveaway_id = context.user_data["buy_giveaway_id"]
    participant_id = context.user_data["buy_participant_id"]

    payload = f"votes:{giveaway_id}:{participant_id}:{votes}"

    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=constants.stars_invoice_title(votes),
        description=constants.stars_invoice_description(votes),
        payload=payload,
        provider_token="",  # empty for Telegram Stars (currency="XTR")
        currency="XTR",
        prices=[LabeledPrice(label=f"{votes} votes", amount=stars_amount)],
    )
    return ConversationHandler.END


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if not query.invoice_payload.startswith("votes:"):
        await query.answer(ok=False, error_message="This purchase is no longer valid.")
        return
    await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    store: Store = context.bot_data["store"]
    payment = update.message.successful_payment
    parts = payment.invoice_payload.split(":")
    if len(parts) != 4 or parts[0] != "votes":
        log.warning("Unrecognized Stars payment payload: %s", payment.invoice_payload)
        return

    _label, giveaway_id_str, participant_id_str, votes_str = parts
    try:
        giveaway_id = ObjectId(giveaway_id_str)
        participant_id = ObjectId(participant_id_str)
        votes = int(votes_str)
    except (InvalidId, ValueError):
        log.warning("Malformed Stars payment payload: %s", payment.invoice_payload)
        return

    giveaway = await store.giveaways.find_one({"_id": giveaway_id})
    participant = await store.get_participant_by_id(participant_id)
    if giveaway is None or participant is None:
        return

    user_id = update.effective_user.id
    new_total = await store.adjust_votes(giveaway_id, user_id, votes, label_fallback=participant["full_name"])

    if participant.get("card_message_id"):
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

    await update.message.reply_text(
        constants.stars_payment_success(votes, new_total), parse_mode=ParseMode.HTML
    )