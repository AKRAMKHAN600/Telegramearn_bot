from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8194601128:AAFKzTW7SVDwlrdN45pseT5kELesqlXDZEQ"
CHANNEL_LINK = "https://t.me/onlineearning2026toinfinite"
CHANNEL_USERNAME = "@onlineearning2026toinfinite"
REFERRAL_REWARD = 10
DAILY_BONUS = 5
MIN_WITHDRAW = 100

users = {}

# Helper to check if user is joined channel
async def is_user_in_channel(app: Application, user_id: int) -> bool:
    try:
        member = await app.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # Referral check
    ref = context.args[0] if context.args else None

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": [], "last_bonus": None}

        # Add referral reward
        if ref and ref.isdigit():
            ref_id = int(ref)
            if ref_id != user_id and ref_id in users:
                if user_id not in users[ref_id]["referrals"]:
                    users[ref_id]["referrals"].append(user_id)
                    users[ref_id]["balance"] += REFERRAL_REWARD
                    await context.bot.send_message(ref_id, f"🎉 You got ₹{REFERRAL_REWARD} for referring {user.first_name}!")

    # Force user to join channel
    if not await is_user_in_channel(context.application, user_id):
        join_button = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Join Channel", url=CHANNEL_LINK)],
                                            [InlineKeyboardButton("✅ I've Joined", callback_data="check_joined")]])
        await update.message.reply_text("🔒 Please join our channel to use the bot:", reply_markup=join_button)
        return

    # Main menu
    await send_main_menu(update, context)

# Main menu buttons
def get_main_menu():
    buttons = [
        [InlineKeyboardButton("💰 Balance", callback_data="balance"),
         InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")],
        [InlineKeyboardButton("👥 My Referral Link", callback_data="referral"),
         InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("ℹ️ How to Earn", callback_data="howto")]
    ]
    return InlineKeyboardMarkup(buttons)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_user.id, f"👋 Welcome to *Refer to earn🤑easy😈* bot!", parse_mode="Markdown", reply_markup=get_main_menu())

# Button handling
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not await is_user_in_channel(context.application, user_id):
        join_button = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Join Channel", url=CHANNEL_LINK)],
                                            [InlineKeyboardButton("✅ I've Joined", callback_data="check_joined")]])
        await query.edit_message_text("🔒 Please join our channel to use the bot:", reply_markup=join_button)
        return

    data = query.data

    if data == "check_joined":
        if await is_user_in_channel(context.application, user_id):
            await query.edit_message_text("✅ Thank you for joining! Now you can use the bot.")
            await send_main_menu(update, context)
        else:
            await query.edit_message_text("❌ You haven't joined yet. Please join and then click again.")
    elif data == "balance":
        bal = users[user_id]["balance"]
        await query.edit_message_text(f"💰 Your current balance: ₹{bal}", reply_markup=get_main_menu())
    elif data == "referral":
        link = f"https://t.me/Refertoearn2026_bot?start={user_id}"
        count = len(users[user_id]["referrals"])
        await query.edit_message_text(f"👥 You referred {count} user(s).\n\n🔗 Your referral link:\n{link}", reply_markup=get_main_menu())
    elif data == "withdraw":
        bal = users[user_id]["balance"]
        if bal >= MIN_WITHDRAW:
            users[user_id]["balance"] = 0
            await query.edit_message_text(f"✅ ₹{bal} withdrawal request received. You will be paid soon.", reply_markup=get_main_menu())
        else:
            await query.edit_message_text(f"❌ Minimum withdrawal is ₹{MIN_WITHDRAW}. You have ₹{bal}.", reply_markup=get_main_menu())
    elif data == "bonus":
        now = datetime.now()
        last = users[user_id]["last_bonus"]
        if not last or (now - last).days >= 1:
            users[user_id]["balance"] += DAILY_BONUS
            users[user_id]["last_bonus"] = now
            await query.edit_message_text(f"🎁 You received ₹{DAILY_BONUS} daily bonus!", reply_markup=get_main_menu())
        else:
            wait_time = 24 - (now - last).seconds // 3600
            await query.edit_message_text(f"⏳ You already claimed today's bonus. Try again in {wait_time} hour(s).", reply_markup=get_main_menu())
    elif data == "howto":
        text = ("📌 *How to Earn:*\n\n"
                "1. 🔗 Share your referral link with friends.\n"
                f"2. 🎯 Earn ₹{REFERRAL_REWARD} per referral.\n"
                f"3. 🎁 Get ₹{DAILY_BONUS} daily bonus.\n"
                f"4. 💸 Withdraw once you reach ₹{MIN_WITHDRAW}.\n\n"
                f"📢 Must join our channel: {CHANNEL_LINK}")
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

# Fallback handler
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ I didn't understand that. Please use the buttons.")

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()
