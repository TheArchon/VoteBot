"""
Yeon's persona, premium emoji pack, and message templates.

The provided 200-emoji pack leans decorative/cute (gifts, hearts, charms,
flowers) rather than functional UI icons (no checkmark/clock glyphs in the
set) — fitting for a lucky-draw giveaway bot. PREMIUM_EMOJI below curates a
semantic subset for common UI slots; FULL_EMOJI_CATALOG keeps the entire
pack available for later use (e.g. decorative flourishes).
"""
from __future__ import annotations

BOT_NAME = "Yeon"

# --- Curated semantic emoji (id, fallback glyph) --------------------------
PREMIUM_EMOJI = {
    "gift": ("5422694848866061927", "🎁"),
    "gift2": ("5424927445880960845", "🎁"),
    "heart": ("5422418630929316184", "💖"),
    "heart2": ("5422631674192101311", "❤️"),
    "sparkle": ("5422714867708624901", "🌟"),
    "clover": ("5206647874934310969", "🍀"),
    "crystal": ("5422844365267565429", "🔮"),
    "card": ("5422551512922488600", "🃏"),
    "medal": ("5453969817168022978", "🏅"),
    "pin": ("5422357698228290320", "📍"),
    "moon": ("5325726727979171396", "🌙"),
    "ribbon": ("5424684827473376419", "🎀"),
    "bouquet": ("5424756476117807727", "💐"),
    "cupcake": ("5422358875049331056", "🧁"),
    "candle": ("5424586507082035363", "🕯"),
    "paperclip": ("5422883410815254311", "📎"),
    "eagle": ("5193181047927379591", "🦅"),
}

# Full 200-emoji pack, kept for future/decorative use — (id, fallback) pairs.
FULL_EMOJI_CATALOG = [
    ("5422694848866061927", "🎁"), ("5422537279400868395", "🎁"), ("5422873888872758210", "📼"),
    ("5422418630929316184", "💖"), ("5422551512922488600", "🃏"), ("5422869288962784257", "💊"),
    ("5422357698228290320", "📍"), ("5424927445880960845", "🎁"), ("5424892626581091101", "🎁"),
    ("5422411664492362253", "🎁"), ("5422424094127720186", "🎁"), ("5422631674192101311", "❤️"),
    ("5422462160422862558", "🎁"), ("5422485795627892255", "🧪"), ("5424586507082035363", "🕯"),
    ("5408874795158775963", "🔮"), ("5328033559208822003", "🎁"), ("5425138041012382757", "🐈‍⬛"),
    ("5422358875049331056", "🧁"), ("5422826721541914133", "❤️"), ("5424756476117807727", "💐"),
    ("5424633786082029327", "🔤"), ("5424656828581574566", "🍄"), ("5422499548113174711", "🍪"),
    ("5422826811736228126", "🎁"), ("5422731703980423582", "🎁"), ("5424816816113350289", "🎁"),
    ("5422852070438895301", "🐈‍⬛"), ("5422527267832103807", "🎁"), ("5422631931890137850", "🌸"),
    ("5425064244884305467", "🎁"), ("5422883410815254311", "📎"), ("5422802180098785566", "❤️"),
    ("5422680830092804870", "🍫"), ("5422849922955245502", "❤️"), ("5422846478391475459", "🌺"),
    ("5422739014014764143", "🎁"), ("5425001628556097182", "❤️"), ("5424838724741528613", "💐"),
    ("5424586051815502630", "💖"), ("5425124335771741136", "🔤"), ("5425000623533748383", "🎁"),
    ("5424654509299232123", "🍄"), ("5424612375670059426", "🎁"), ("5422427671835474966", "🎁"),
    ("5303428391649711374", "🥊"), ("5422736570178371979", "🎁"), ("5325726727979171396", "🌙"),
    ("5422802171508850526", "🎁"), ("5422647595635866664", "🐈‍⬛"), ("5422607575130600359", "🎁"),
    ("5422573279816747511", "🎁"), ("5422484648871626179", "🧪"), ("5425035421358781637", "🎁"),
    ("5422844365267565429", "🔮"), ("5422369784266257729", "💐"), ("5422586993647320155", "❤️"),
    ("5424632072390078052", "🩸"), ("5424966508608517502", "🧛"), ("5422364020420151066", "🎁"),
    ("5422750640491230076", "🕯"), ("5422585039437197830", "🎁"), ("5422875516665364578", "💖"),
    ("5425141511345961001", "📍"), ("5422568121561020434", "🎁"), ("5422737811423918818", "📎"),
    ("5422371566677687396", "🎁"), ("5425004944270850753", "💀"), ("5422455550468193436", "🎁"),
    ("5422810409256126902", "🍭"), ("5422411535643345371", "🎁"), ("5422738288165286717", "🎁"),
    ("5424656373315040194", "🎂"), ("5422412218543145762", "🔮"), ("5422716078889401699", "💀"),
    ("5422728328136129501", "🔤"), ("5422356508522349013", "🍄"), ("5422870830856045306", "🐈‍⬛"),
    ("5422609769858889724", "💖"), ("5422426177186854148", "🎁"), ("5422363943110737710", "📎"),
    ("5424684827473376419", "🎀"), ("5424719341830567516", "💐"), ("5422479829918317452", "🍫"),
    ("5422666648110793395", "❤️"), ("5422807926765029627", "🍭"), ("5422607012489889076", "🎁"),
    ("5422809404233775999", "🎁"), ("5323604906760766133", "🎁"), ("5325961250373402218", "🧱"),
    ("5323778036892468288", "🎁"), ("5323307085138526090", "👠"), ("5323657378376222067", "🎁"),
    ("5323714514326158336", "🎁"), ("5424941318625333234", "🎂"), ("5323336999585742625", "🌙"),
    ("5422796248748948435", "🎁"), ("5422470088932491424", "🎁"), ("5422423492832294676", "💍"),
    ("5422729595151483494", "🎁"), ("5422473889978549304", "🌸"), ("5422351638029437496", "🐈‍⬛"),
    ("5422808841593061325", "🕯"), ("5422657499830453811", "🎂"), ("5422609391901770006", "🍄"),
    ("5424907822175383816", "🎁"), ("5361646256735157530", "🎩"), ("5422646693692736744", "🎀"),
    ("5422866011902739741", "📎"), ("5422344297930326583", "🎁"), ("5325755143482801350", "🎁"),
    ("5323276092654520315", "🎁"), ("5199559490973765965", "🎃"), ("5332791446669917319", "🤩"),
    ("5323608729281659506", "🎁"), ("5424978787920021797", "🍽"), ("5325885396955988038", "🎁"),
    ("5323266338783787640", "🎁"), ("5303064238552552304", "🥊"), ("5424655363997731609", "🎁"),
    ("5422627838786306160", "🎁"), ("5422515164614262883", "📎"), ("5422604328135324172", "🎀"),
    ("5422389773044053533", "🎁"), ("5422693229663387089", "🎁"), ("5422643618496149287", "🍄"),
    ("5422789535715064830", "🐈‍⬛"), ("5424658391949671561", "🌸"), ("5422531794727635072", "🎁"),
    ("5425108740745490495", "🎁"), ("5422781594320535939", "💖"), ("5422784373164375309", "🔤"),
    ("5422341433187140040", "🎁"), ("5424777207924946177", "🕯"), ("5201941393936776694", "🎃"),
    ("5422681942489332796", "🎁"), ("5422714867708624901", "🌟"), ("5325824584514044667", "👠"),
    ("5425079118356053348", "🔤"), ("5422878175250119584", "🐈‍⬛"), ("5424812791728991782", "🌸"),
    ("5422864787837057732", "🍭"), ("5422649648630233281", "🎁"), ("5425103595374669922", "🧁"),
    ("5424754680821477240", "🎁"), ("5422587822576009874", "🎁"), ("5422636639174293981", "💖"),
    ("5422581569103626576", "❤️"), ("5422540251518241028", "🎁"), ("5424671633333845534", "🎁"),
    ("5424818126078372040", "🎁"), ("5422559269633421747", "💐"), ("5422851963064713343", "🎁"),
    ("5424836972394868326", "🍄"), ("5422590708794032216", "🕯"), ("5422609576585364592", "🔤"),
    ("5422488522932125845", "💖"), ("5422561691994981960", "🎁"), ("5422683106425470094", "💐"),
    ("5422756631970610806", "🎁"), ("5422490197969370168", "❤️"), ("5422780176981329483", "🎁"),
    ("5424833489176392720", "🐰"), ("5422614498617887805", "🍪"), ("5422543090491621908", "🥚"),
    ("5424681095146795110", "🧁"), ("5424864597624516345", "🐈‍⬛"), ("5425059357211522940", "🎁"),
    ("5325640128553582170", "🎁"), ("5325708143655685239", "🎁"), ("5325908692858600026", "🎁"),
    ("5325758837154676265", "👠"), ("5323499963529857358", "🎁"), ("5325510459195953188", "🌙"),
    ("5326049357332513437", "🧱"), ("5323574945068913378", "🎁"), ("5431903945943446170", "🍄"),
    ("5431768929351530943", "🧁"), ("5431752024360251517", "💐"), ("5431777699674748608", "🐸"),
    ("5429618580960344466", "🎁"), ("5431786134990516186", "🐈‍⬛"), ("5431848824333169634", "🎁"),
    ("5431619391475184797", "🎁"), ("5431492393587210182", "🎁"), ("5431650864995529681", "🎁"),
    ("5431478731296240530", "🎁"), ("5431409736941597411", "🎁"), ("5429118771321138241", "🎂"),
    ("5429175761242193523", "🎁"), ("5429629022025845517", "🎁"), ("5429626337671281265", "📍"),
    ("5206647874934310969", "🍀"), ("5453969817168022978", "🏅"), ("5425054924805280757", "💖"),
    ("5206438637012548993", "💐"), ("5206496863884181895", "💐"), ("5203951816588430946", "💐"),
    ("5206406875729401557", "💐"), ("5193181047927379591", "🦅"),
]


def pe(name: str) -> str:
    """Return the <tg-emoji> HTML snippet for a named premium emoji."""
    emoji_id, fallback = PREMIUM_EMOJI[name]
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


# --- Economy defaults --------------------------------------------------
JOIN_BUTTON_TEXT = "JOIN GIVEAWAY"

# --- Message templates ------------------------------------------------------

def welcome_panel(channel_connected: bool) -> str:
    lines = [
        f'{pe("sparkle")} <b>Welcome to {BOT_NAME}</b>',
        "",
        f'<blockquote>{pe("gift")} Create powerful vote giveaways',
        f'{pe("crystal")} Real-time vote system with anti-cheat',
        f'{pe("card")} Every participant gets their own shareable voting card',
        f'{pe("medal")} Leaderboard & full management tools</blockquote>',
        "",
    ]
    if channel_connected:
        lines.append(f'{pe("clover")} Ready to go ~ tap <b>CREATE</b> to start a giveaway.')
    else:
        lines.append(f'{pe("pin")} Tap <b>CONNECT</b> first to link your channel.')
    return "\n".join(lines)


def connect_prompt() -> str:
    return "\n".join([
        f'{pe("pin")} <b>Connect your channel</b>',
        "",
        f'{pe("card")} Send the channel\'s username or ID:',
        "",
        f'<blockquote>Public: <code>@yourchannel</code></blockquote>',
        f'<blockquote>Private: <code>-1001234567890</code></blockquote>',
        "",
        f'{pe("moon")} Make sure {BOT_NAME} is an <b>admin</b> there first, '
        f'with permission to post messages.',
    ])


def connect_failed() -> str:
    return (
        f'{pe("card")} Couldn\'t verify that channel. Make sure the ID/username '
        f'is correct and {BOT_NAME} has been added there as an <b>admin</b> '
        f'with post permissions, then try again.'
    )


def connect_success(channel_title: str) -> str:
    return (
        f'{pe("sparkle")} <b>Connected!</b>\n'
        f'{pe("pin")} Channel: <b>{channel_title}</b>\n\n'
        f'{pe("gift")} Tap <b>CREATE</b> to start your first giveaway.'
    )


def create_no_channel() -> str:
    return (
        f'{pe("pin")} No channel connected yet. Tap <b>CONNECT</b> from the '
        f"main menu first."
    )


def create_prize_prompt() -> str:
    return "\n".join([
        f'{pe("gift")} <b>Create Giveaway</b>',
        "",
        f'{pe("card")} Send the prize message now — text, image, formatting, '
        f'anything. This is exactly what gets posted.',
        "",
        f'{pe("moon")} Or send <code>SKIP</code> to use a default template.',
    ])


def default_giveaway_announcement() -> str:
    return "\n".join([
        f'🦄 <b>EXCLUSIVE GIVEAWAY</b>',
        "",
        f'🦋 A brand new giveaway just dropped ~ tap below to join '
        f'and start collecting votes!',
    ])


def giveaway_created(code: str, channel_title: str, link: str) -> str:
    return "\n".join([
        f'{pe("sparkle")} <b>GIVEAWAY CREATED!</b>',
        "",
        f'{pe("crystal")} ID: <code>{code}</code>',
        f'{pe("pin")} Channel: {channel_title}',
        "",
        f'{pe("card")} Link:',
        link,
    ])


def create_post_failed() -> str:
    return (
        f'{pe("card")} Could not post to the channel — double check '
        f'{BOT_NAME} is still an admin there with post permissions.'
    )


def manage_no_channel() -> str:
    return f'{pe("pin")} Connect a channel first — tap <b>CONNECT</b> from the main menu.'


def manage_no_giveaway() -> str:
    return (
        f'{pe("card")} No giveaway yet on this channel. Tap <b>CREATE</b> from '
        f"the main menu to start one."
    )


def management_panel(status: str, channel_title: str, joined: int) -> str:
    status_flag = f'{pe("clover")} ACTIVE' if status == "active" else f'{pe("moon")} ENDED'
    return "\n".join([
        f'{pe("crystal")} <b>Management Panel</b>',
        "",
        f'Status: {status_flag}',
        f'Channel: {channel_title}',
        f'Joined: <b>{joined}</b>',
    ])


def add_votes_prompt() -> str:
    return "\n".join([
        f'{pe("gift")} <b>Add Votes</b>',
        "",
        f'Send: <code>USER_ID VOTES</code>',
        f'Example: <code>12345678 10</code>',
    ])


def remove_votes_prompt() -> str:
    return "\n".join([
        f'{pe("card")} <b>Remove Votes</b>',
        "",
        f'Send: <code>USER_ID VOTES</code>',
        f'Example: <code>12345678 5</code>',
    ])


def vote_adjust_bad_format() -> str:
    return f'{pe("card")} Send it as <code>USER_ID VOTES</code> — both numbers, separated by a space.'


def votes_added(user_id: int, amount: int, new_total: int) -> str:
    return (
        f'{pe("sparkle")} Added <b>{amount}</b> votes to <code>{user_id}</code>. '
        f'New total: <b>{new_total}</b>'
    )


def votes_removed(user_id: int, amount: int, new_total: int) -> str:
    return (
        f'{pe("moon")} Removed <b>{amount}</b> votes from <code>{user_id}</code>. '
        f'New total: <b>{new_total}</b>'
    )


def leaderboard_empty() -> str:
    return f'{pe("card")} No participants yet.'


def leaderboard(entries: list[tuple[str, int]]) -> str:
    lines = [f'{pe("medal")} <b>Leaderboard</b>', ""]
    medals = [pe("medal"), pe("ribbon"), pe("bouquet")]
    for i, (label, votes) in enumerate(entries, start=1):
        rank_icon = medals[i - 1] if i <= 3 else f"{i}."
        lines.append(f'{rank_icon} {label} — <b>{votes}</b> votes')
    return "\n".join(lines)


def giveaway_ended(winner_label: str | None) -> str:
    if winner_label:
        return (
            f'{pe("sparkle")} <b>Giveaway ended!</b>\n'
            f'{pe("medal")} Winner: <b>{winner_label}</b> {pe("heart")}'
        )
    return f'{pe("moon")} <b>Giveaway ended.</b> No participants — no winner this time.'


def logger_giveaway_created(owner_label: str, channel_title: str) -> str:
    return f'{pe("gift")} <b>Giveaway created</b> by {owner_label} in {channel_title}.'


def logger_giveaway_ended(owner_label: str) -> str:
    return f'{pe("moon")} <b>Giveaway ended</b> by {owner_label}.'


# --- Join / voting card templates ------------------------------------------

def join_needs_gate(channel_link: str) -> str:
    return "\n".join([
        f'{pe("pin")} <b>Join the channel first</b>',
        "",
        f'{pe("card")} You need to be a member of the giveaway channel to '
        f'participate. Join, then tap the button again.',
        "",
        channel_link,
    ])


def join_no_giveaway() -> str:
    return f'{pe("card")} This giveaway isn\'t active anymore.'


def join_already_joined() -> str:
    return f'{pe("clover")} You\'re already in this giveaway — check the channel for your card!'


def registration_success(share_link: str) -> str:
    return "\n".join([
        f'{pe("sparkle")} <b>Registration Successful!</b>',
        "",
        f'<blockquote>{pe("card")} Your voting card is live in the channel.',
        f'{pe("heart")} Share your link to get max votes and win:</blockquote>',
        share_link,
    ])


def voting_card(full_name: str, user_id: int, votes: int) -> str:
    return "\n".join([
        f'🦄<b>EXCLUSIVE GIVEAWAY ENTRY</b>',
        "",
        f'<blockquote>{pe("card")} Participant: <b>{full_name}</b>',
        f'🪼 User ID: <code>{user_id}</code>',
        f'🦋 Votes: <b>{votes}</b></blockquote>',
        "",
        f'🌛 Tap below to vote for them!',
    ])


def vote_button_text(votes: int) -> str:
    return f"VOTE ({votes})"


def vote_needs_gate() -> str:
    return "Join the channel first to vote!"


def vote_already_voted() -> str:
    return "You've already voted for this person."


def vote_recorded() -> str:
    return "Vote recorded! 🌙"


def vote_gone() -> str:
    return "This entry is no longer active."

# --- Anti-cheat: voter-leave detection --------------------------------------
# --- Anti-cheat: suspicious vote blocking ------------------------------

def vote_blocked_suspicious() -> str:
    return "This vote looks automated/suspicious and wasn't counted."


def anticheat_voter_warning() -> str:
    return "\n".join([
        f'{pe("moon")} <b>Vote not counted</b>',
        "",
        f'{pe("card")} Your vote looked automated or suspicious (e.g. a brand-new '
        f'account, or voting seconds after joining the channel), so it wasn\'t counted.',
        "",
        f'{pe("pin")} If this was a mistake, vote normally from your regular account '
        f'after being a channel member for a bit — genuine votes are always counted.',
    ])


def anticheat_owner_report(participant_label: str, voter_id: int, reasons: list[str], blocked_total: int) -> str:
    reason_lines = "\n".join(f'• {r}' for r in reasons)
    return "\n".join([
        f'{pe("moon")} <b>Suspicious vote blocked</b>',
        "",
        f'{pe("card")} For: <b>{participant_label}</b>',
        f'{pe("pin")} Voter ID: <code>{voter_id}</code>',
        "",
        f'<blockquote>{reason_lines}</blockquote>',
        "",
        f'{pe("crystal")} Total suspicious votes blocked for this participant so far: <b>{blocked_total}</b>',
        "",
        f'{pe("gift")} No automatic action taken on the participant — review and '
        f'disqualify/remove their card manually from MANAGE if this looks like abuse.',
    ])

def vote_revoked_notice(participant_label: str, new_total: int) -> str:
    return (
        f'{pe("moon")} A vote for <b>{participant_label}</b> was removed — '
        f'the voter left the channel.\n'
        f'{pe("card")} Current votes: <b>{new_total}</b>'
    )


# --- Buy votes: cash flow ---------------------------------------------------
 
def buy_qty_prompt(method: str) -> str:
    label = "cash" if method == "cash" else "Telegram Stars"
    return f'{pe("gift")} How many votes would you like to buy with {label}? Send a number.'
 
 
def buy_qty_invalid() -> str:
    return f'{pe("card")} Send a whole number greater than 0.'
 
 
def buy_cash_qr_caption(votes: int, rupees: float) -> str:
    return "\n".join([
        f'{pe("sparkle")} <b>Pay ₹{rupees:g} for {votes} votes</b>',
        "",
        f'{pe("pin")} Scan the QR above, complete the payment, then send a '
        f'screenshot of it right here.',
    ])
 
 
def buy_cash_awaiting_screenshot() -> str:
    return f'{pe("card")} Send a screenshot of your payment to continue.'
 
 
def buy_cash_submitted() -> str:
    return (
        f'{pe("moon")} <b>Payment submitted!</b> The owner will review it '
        f"shortly — you'll hear back here."
    )
 
 
def logger_purchase_review(buyer_label: str, votes: int, rupees: float) -> str:
    return "\n".join([
        f'{pe("gift")} <b>Vote purchase review</b>',
        "",
        f'{pe("card")} Buyer: {buyer_label}',
        f'{pe("sparkle")} Votes requested: <b>{votes}</b>',
        f'{pe("pin")} Amount: ₹{rupees:g}',
    ])
 
 
def purchase_votes_credited(votes: int, new_total: int) -> str:
    return (
        f'{pe("sparkle")} <b>+{votes} votes added!</b> New total: <b>{new_total}</b>\n'
        f'{pe("heart")} Thanks for your purchase — keep enjoying and participating!'
    )
 
 
def purchase_rejected() -> str:
    return (
        f'{pe("moon")} Your payment couldn\'t be verified and was rejected. '
        f"Contact the giveaway owner if you think this is a mistake."
    )
 
 
def purchase_review_resolved_accept(buyer_label: str) -> str:
    return f'{pe("sparkle")} Accepted — {buyer_label} has been asked to share their link.'
 
 
def purchase_review_resolved_reject(buyer_label: str) -> str:
    return f'{pe("moon")} Rejected — {buyer_label} has been notified.'
 
 
# --- Buy votes: Telegram Stars flow -----------------------------------------
 
def stars_invoice_title(votes: int) -> str:
    return f"{votes} Giveaway Votes"
 
 
def stars_invoice_description(votes: int) -> str:
    return f"Instantly adds {votes} votes to your giveaway entry."
 
 
def stars_payment_success(votes: int, new_total: int) -> str:
    return (
        f'{pe("sparkle")} <b>Payment received!</b> +{votes} votes added.\n'
        f'{pe("card")} New total: <b>{new_total}</b>\n'
        f'{pe("heart")} Thanks for your purchase — keep enjoying and participating!'
    )
 