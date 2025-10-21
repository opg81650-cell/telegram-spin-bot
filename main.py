# pip install python-telegram-bot==20.*
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random, sqlite3, datetime, os

TOKEN = os.getenv("8391185427:AAEwRTJk1n0NtqqRyUXcTAPe-XKgKOrChmk")

# Create a simple database
conn = sqlite3.connect("data.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, spins INTEGER DEFAULT 1, referred_by INTEGER)")
conn.commit()

def add_user(user_id, ref=None):
    user = conn.execute("SELECT id FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        conn.execute("INSERT INTO users (id, referred_by) VALUES (?, ?)", (user_id, ref))
        conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    ref = int(args[0]) if args else None
    add_user(user_id, ref)
    text = (
        "🎡 *Welcome to Lucky Spin Bot!* 🎁\n\n"
        "Spin the wheel and win coins!\n\n"
        "🎯 /spin – Try your luck\n"
        "💰 /balance – Check your balance\n"
        "👫 /invite – Invite friends and earn!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    u = conn.execute("SELECT spins, balance FROM users WHERE id=?", (user_id,)).fetchone()
    if not u:
        await update.message.reply_text("Use /start first.")
        return
    spins, balance = u
    if spins <= 0:
        await update.message.reply_text("No spins left! Invite friends using /invite to earn more.")
        return
    prize = random.choice([0, 5, 10, 20, 50, 100])
    conn.execute("UPDATE users SET spins=spins-1, balance=balance+? WHERE id=?", (prize, user_id))
    conn.commit()
    if prize == 0:
        msg = "😞 No luck this time!"
    else:
        msg = f"🎉 You won {prize} coins!"
    await update.message.reply_text(msg)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    u = conn.execute("SELECT balance, spins FROM users WHERE id=?", (user_id,)).fetchone()
    if not u:
        await update.message.reply_text("Use /start first.")
        return
    balance, spins = u
    await update.message.reply_text(f"💰 Balance: {balance} coins\n🎡 Spins left: {spins}")

async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(f"👫 Invite your friends!\nWhen they join, you get +1 spin.\n\nYour link:\n{link}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("spin", spin))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("invite", invite))

app.run_polling()
