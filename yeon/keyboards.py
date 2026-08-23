from __future__ import annotations

from telegram import InlineKeyboardButton as Btn
from telegram import InlineKeyboardMarkup as Markup

from . import constants


def pbtn(
    text: str,
    *,
    url: str | None = None,
    callback_data: str | None = None,
    style: str | None = None,
    icon_key: str | None = None,
) -> Btn:
    icon_id = None
    if icon_key and icon_key in constants.PREMIUM_EMOJI:
        icon_id, _fallback = constants.PREMIUM_EMOJI[icon_key]
    return Btn(text=text, url=url, callback_data=callback_data, style=style, icon_custom_emoji_id=icon_id)


def main_menu_keyboard() -> Markup:
    return Markup([
        [pbtn("CONNECT", callback_data="menu_connect", style="success", icon_key="pin")],
        [
            pbtn("CREATE", callback_data="menu_create", style="primary", icon_key="gift"),
            pbtn("MANAGE", callback_data="menu_manage", style="primary", icon_key="crystal"),
        ],
    ])


def cancel_keyboard() -> Markup:
    return Markup([[pbtn("CANCEL", callback_data="menu_cancel", style="danger")]])


def giveaway_created_keyboard() -> Markup:
    return Markup([
        [pbtn("MANAGE", callback_data="menu_manage", style="primary", icon_key="crystal")],
        [pbtn("MAIN MENU", callback_data="menu_home", icon_key="moon")],
    ])


def management_panel_keyboard() -> Markup:
    return Markup([
        [
            pbtn("ADD VOTES", callback_data="menu_addvotes", style="success", icon_key="sparkle"),
            pbtn("REMOVE VOTES", callback_data="menu_removevotes", style="danger", icon_key="moon"),
        ],
        [pbtn("LEADERBOARD", callback_data="menu_leaderboard", style="primary", icon_key="medal")],
        [pbtn("END GIVEAWAY", callback_data="menu_end_confirm", style="danger", icon_key="card")],
        [pbtn("BACK", callback_data="menu_home")],
    ])


def end_confirm_keyboard() -> Markup:
    return Markup([[
        pbtn("YES, END IT", callback_data="menu_end_yes", style="danger"),
    ],
    [
        pbtn("CANCEL", callback_data="menu_manage"),
    ],
    ])


def back_to_manage_keyboard() -> Markup:
    return Markup([[pbtn("BACK", callback_data="menu_manage")]])


def join_giveaway_keyboard(bot_username: str, giveaway_code: str) -> Markup:
    """Deep-links into the bot's DM with the giveaway code as the /start payload."""
    url = f"https://t.me/{bot_username}?start=join_{giveaway_code}"
    return Markup([[pbtn(constants.JOIN_BUTTON_TEXT, url=url, style="primary", icon_key="gift")]])


def append_join_button(existing_markup: Markup | None, bot_username: str, giveaway_code: str) -> Markup:
    """Preserves whatever buttons the owner's crafted message already had
    and adds the Join Giveaway row underneath."""
    rows = list(existing_markup.inline_keyboard) if existing_markup else []
    url = f"https://t.me/{bot_username}?start=join_{giveaway_code}"
    rows.append([pbtn(constants.JOIN_BUTTON_TEXT, url=url, style="primary", icon_key="gift")])
    return Markup(rows)


def voting_card_keyboard(participant_id: str, votes: int) -> Markup:
    return Markup([[
        pbtn(constants.vote_button_text(votes), callback_data=f"vote_{participant_id}", style="success", icon_key="heart")
    ]])


def registration_success_keyboard() -> Markup:
    return Markup([[
        pbtn("BUY VOTES (CASH)", callback_data="buyvotes_cash", style="primary", icon_key="gift"),
    ],
    [
        pbtn("BUY VOTES (STARS)", callback_data="buyvotes_stars", style="primary", icon_key="sparkle"),
    ],
    ])

def purchase_review_keyboard(purchase_id: str) -> Markup:
    return Markup([[
        pbtn("ACCEPT", callback_data=f"purchase_accept_{purchase_id}", style="success", icon_key="sparkle"),
        pbtn("REJECT", callback_data=f"purchase_reject_{purchase_id}", style="danger", icon_key="moon"),
    ]])