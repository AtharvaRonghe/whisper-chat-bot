from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatAction

# DATABASE
from database_utils import init_db, upsert_user, get_user, add_report

# =========================
# INIT DATABASE
# =========================
init_db()

# =========================
# GLOBAL MEMORY (RUNTIME)
# =========================
users = {}
waiting_males = []
waiting_females = []
waiting_others = []

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    users[user_id] = {"partner": None}

    await update.message.reply_text(
        "👋 *Welcome to Whisper Chat*\n\n"
        "Speak freely. Stay anonymous.\n"
        "No profiles. No names.\n\n"
        "👇 Select your gender to begin:",
        parse_mode="Markdown",
        reply_markup=gender_keyboard()
    )

# =========================
# GENDER
# =========================
def gender_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚹 Male", callback_data="gender_male")],
        [InlineKeyboardButton("🚺 Female", callback_data="gender_female")],
        [InlineKeyboardButton("⚧ Other", callback_data="gender_other")]
    ])

async def set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    gender = query.data.split("_")[1]

    users.setdefault(user_id, {})["gender"] = gender

    if gender in ["female", "other"]:
        users[user_id]["nsfw_allowed"] = False
        upsert_user(user_id, gender=gender, nsfw_allowed=0)

        await query.message.reply_text(
            "🔒 *NSFW is OFF by default*\n\nYou can enable it anytime 👇",
            parse_mode="Markdown",
            reply_markup=nsfw_toggle()
        )
    else:
        users[user_id]["nsfw_allowed"] = True
        upsert_user(user_id, gender=gender, nsfw_allowed=1)

        await query.message.reply_text("✅ You can now use /find to chat.")

# =========================
# NSFW
# =========================
def nsfw_toggle():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 ALLOW NSFW", callback_data="nsfw_on")],
        [InlineKeyboardButton("🔒 KEEP NSFW OFF", callback_data="nsfw_off")]
    ])

async def toggle_nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    allow = query.data == "nsfw_on"

    users[user_id]["nsfw_allowed"] = allow
    upsert_user(user_id, nsfw_allowed=int(allow))

    await query.message.reply_text(
        f"NSFW is now {'ENABLED 🔓' if allow else 'DISABLED 🔒'}"
    )

# =========================
# SETTINGS
# =========================
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if users.get(user_id, {}).get("partner"):
        await update.message.reply_text(
            "❗ End the current chat before changing settings.\nUse /stop"
        )
        return

    await update.message.reply_text(
        "⚙️ *Whisper Chat – Settings*\n\nChoose what to change:",
        parse_mode="Markdown",
        reply_markup=settings_keyboard()
    )

def settings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Change Gender", callback_data="settings_gender")],
        [InlineKeyboardButton("🎂 Change Age", callback_data="settings_age")],
        [InlineKeyboardButton("❌ Cancel", callback_data="settings_cancel")]
    ])

async def settings_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "settings_gender":
        await query.message.reply_text(
            "Select your new gender:",
            reply_markup=gender_keyboard()
        )

    elif query.data == "settings_age":
        context.user_data["awaiting_age"] = True
        await query.message.reply_text("Enter your age:")

    elif query.data == "settings_cancel":
        await query.message.reply_text("❌ Settings closed.")

# =========================
# FIND MATCH
# =========================
async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    gender = users[user_id]["gender"]
    partner = None

    if gender == "male":
        for q in (waiting_females, waiting_others, waiting_males):
            if q:
                partner = q.pop(0)
                break
    elif gender == "other":
        for q in (waiting_males, waiting_females, waiting_others):
            if q:
                partner = q.pop(0)
                break
    else:
        for q in (waiting_males, waiting_others, waiting_females):
            if q:
                partner = q.pop(0)
                break

    if not partner:
        {"male": waiting_males,
         "female": waiting_females,
         "other": waiting_others}[gender].append(user_id)
        await update.message.reply_text("🔎 Looking for a partner…")
        return

    users[user_id]["partner"] = partner
    users[partner]["partner"] = user_id

    await context.bot.send_message(
        partner, "🎉 You’re now connected!", reply_markup=report_button()
    )
    await update.message.reply_text(
        "🎉 You’re now connected!", reply_markup=report_button()
    )

# =========================
# MESSAGE RELAY
# =========================
async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # AGE INPUT
    if context.user_data.get("awaiting_age"):
        if not text.isdigit():
            await update.message.reply_text("❗ Enter a valid number.")
            return

        upsert_user(user_id, age=int(text))
        context.user_data["awaiting_age"] = False
        await update.message.reply_text(f"✅ Age updated to {text}")
        return

    partner = users.get(user_id, {}).get("partner")
    if not partner:
        await update.message.reply_text(
            "❗ Chat has ended.\n\nWhat next?",
            reply_markup=next_chat_keyboard()
        )
        return

    await context.bot.send_chat_action(partner, ChatAction.TYPING)
    await context.bot.send_message(partner, text)

# =========================
# NEXT CHAT
# =========================
def next_chat_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Next Chat", callback_data="next_chat")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="open_settings")]
    ])

async def next_chat_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.reply_text("🔎 Looking for a partner…")
    await find(update, context)

async def open_settings_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await settings(update, context)

# =========================
# REPORT
# =========================
def report_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚨 Report & Exit Chat", callback_data="report")]
    ])

async def report_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    reporter = query.from_user.id
    partner = users.get(reporter, {}).get("partner")

    if not partner:
        await query.message.reply_text("❗ No active chat.")
        return

    users[reporter]["partner"] = None
    users[partner]["partner"] = None

    add_report(partner)

    await context.bot.send_message(
        partner, "⚠️ You were reported. Chat ended.",
        reply_markup=next_chat_keyboard()
    )

    await query.message.reply_text(
        "✅ Report submitted.\n🚫 Chat ended.",
        reply_markup=next_chat_keyboard()
    )

# =========================
# STOP
# =========================
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner = users.get(user_id, {}).get("partner")

    if partner:
        users[partner]["partner"] = None
        await context.bot.send_message(
            partner, "⚠️ Partner left the chat.",
            reply_markup=next_chat_keyboard()
        )

    users[user_id]["partner"] = None
    await update.message.reply_text(
        "❌ Chat ended.",
        reply_markup=next_chat_keyboard()
    )

# =========================
# STATUS
# =========================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_user(update.effective_user.id)

    if not data:
        await update.message.reply_text("❗ No profile found. Use /start")
        return

    await update.message.reply_text(
        f"👤 Gender: {data['gender']}\n"
        f"🎂 Age: {data['age'] or '-'}\n"
        f"🎚 NSFW: {'ON' if data['nsfw_allowed'] else 'OFF'}\n"
        f"🚨 Reports: {data['reports']}"
    )

# =========================
# BOT START
# =========================
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("find", find))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("settings", settings))
app.add_handler(CommandHandler("status", status))

app.add_handler(CallbackQueryHandler(set_gender, pattern="^gender_"))
app.add_handler(CallbackQueryHandler(toggle_nsfw, pattern="^nsfw_"))
app.add_handler(CallbackQueryHandler(settings_action, pattern="^settings_"))
app.add_handler(CallbackQueryHandler(next_chat_action, pattern="^next_chat$"))
app.add_handler(CallbackQueryHandler(open_settings_action, pattern="^open_settings$"))
app.add_handler(CallbackQueryHandler(report_user, pattern="^report$"))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, relay))

print("🫧 Whisper Chat is live and running...")
app.run_polling()
