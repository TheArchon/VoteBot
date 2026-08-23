# Yeon 연 — Lucky-Draw Giveaway Bot

A Telegram giveaway/voting bot: publish a giveaway to your channel,
participants get their own shareable voting card, votes can be earned by
sharing or purchased with cash/Telegram Stars, and leaving the channel
automatically revokes any votes a person cast.

Fully **button-driven** — no text commands to memorize.

## Build status — all core features done ✅

| Feature | Status |
|---|---|
| CONNECT — link your channel via button | ✅ Done |
| CREATE — start a giveaway, custom or default prize message | ✅ Done |
| JOIN — force-gated participation, own shareable voting card | ✅ Done |
| VOTE — public voting on cards, duplicate/self-vote prevention | ✅ Done |
| MANAGE panel — status, ADD/REMOVE VOTES, LEADERBOARD, END | ✅ Done |
| Anti-cheat — auto vote removal when a voter leaves the channel | ✅ Done |
| Paid votes — Cash (QR + screenshot + owner review) | ✅ Done |
| Paid votes — Telegram Stars (instant) | ✅ Done |

## How it works

**Owner, in the bot's DM — `/start`:**

- **CONNECT** — send your channel's `@username` or numeric ID (bot must
  already be an admin there). Stored in the database — change it anytime.
- **CREATE** — send your prize message (text/image/formatting), or `SKIP`
  for a default template. Posted instantly with a **JOIN GIVEAWAY** button.
- **MANAGE** — live panel: status, channel, participant count, and:
  - **ADD VOTES** / **REMOVE VOTES** — `USER_ID VOTES` manual override
  - **LEADERBOARD** — top participants by votes
  - **END GIVEAWAY** — closes voting, announces the winner

**Participants:**

1. Tap **JOIN GIVEAWAY** → opens the bot DM → must be a channel member
2. Gets their own **voting card** posted to the channel with a live
   **VOTE (n)** button — share it to collect votes from friends
3. Anyone (except themselves) can vote once per card — duplicate/self
   votes are blocked, count updates instantly
4. **Buy Votes** buttons on their confirmation DM: pay with **cash** (QR
   code + screenshot, reviewed by the owner in the logger group with
   Accept/Reject buttons) or **Telegram Stars** (instant, no review needed)

**Anti-cheat:** if a voter leaves the connected channel, every vote they
cast is automatically revoked — the affected card is edited live and a
notice is posted in the channel (auto-deletes after 60 seconds).

## Project structure

```
yeon-bot/
├── yeon/
│   ├── __main__.py
│   ├── app.py                  # wires 5 ConversationHandlers + all callbacks
│   ├── config.py
│   ├── constants.py            # persona, premium emoji pack, message templates
│   ├── keyboards.py
│   ├── storage.py              # MongoDB — channel/giveaway/participant/purchase data
│   ├── utils/
│   │   └── gate.py             # channel-membership check
│   └── handlers/
│       ├── start.py            # /start — owner menu or participant join
│       ├── menu.py             # connect/create/manage/vote button flows
│       ├── payments.py         # buy-votes: cash review + Telegram Stars
│       └── anticheat.py        # voter-leave detection, auto vote revoke
├── assets/qr.jpg               # your cash-payment QR code goes here
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

## Setup

1. Create the bot via [@BotFather](https://t.me/BotFather); grab the token.
2. Get your user id from [@userinfobot](https://t.me/userinfobot).
3. Create a private **logger group**; add the bot as admin.
4. Copy `.env.example` → `.env`, fill in `BOT_TOKEN`, `BOT_USERNAME`,
   `OWNER_ID`, `LOGGER_GROUP_ID`, `MONGO_URI`. Adjust `RUPEES_PER_VOTE` /
   `STARS_PER_VOTE` for your pricing.
5. Drop your payment QR code at `assets/qr.jpg` (or point `QR_IMAGE` at
   your own path).

```bash
pip install -r requirements.txt
python -m yeon
```

Then in the bot's DM: `/start` → **CONNECT** your channel (add the bot as
admin there first) → **CREATE** your first giveaway.

## A note on premium emoji rendering

Telegram restricts custom/premium emoji to **private, group, and
supergroup** chats when relying on the bot owner's Premium subscription —
**channels are excluded** from that exemption. This means:

- **DM messages** (welcome panel, management panel, purchase reviews) show
  real premium emoji, since the owner's account has Premium.
- **Channel posts** (giveaway announcements, voting cards) will show the
  *fallback* (regular) emoji instead, unless the bot itself has purchased
  an additional username via [Fragment](https://fragment.com).

This is a Telegram platform restriction, not a bug — the code already
generates the correct `<tg-emoji>` entities everywhere; whether they
render as premium graphics in a channel depends entirely on that Fragment
requirement being met.

## Premium emoji pack

All 200 provided emoji ids are stored in `yeon/constants.py` under
`FULL_EMOJI_CATALOG`. A curated subset — `PREMIUM_EMOJI` — maps semantic
names (`gift`, `heart`, `sparkle`, `clover`, `crystal`, `card`, `medal`,
`pin`, `moon`, `ribbon`, `bouquet`, `cupcake`, `candle`, `paperclip`,
`eagle`) to specific ids used throughout the bot's messages.

## License

MIT — see `LICENSE`.