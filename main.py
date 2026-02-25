import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# =========================
# KEEP RENDER ALIVE (WEB SERVER)
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# =========================
# DISCORD BOT SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("TOKEN not found!")
    exit(1)

# =========================
# BINGO WORDS
# =========================

BINGO_WORDS = [
    "diddy",
    "epstein",
    "sus",
    "crazy",
    "wild",
    "lol",
    "bruh",
    "nah",
    "what",
    "real",
    "fake",
    "insane",
    "bro",
    "why",
    "no way",
    "stop",
    "wait",
    "serious",
    "joke",
    "cap",
    "facts",
    "ok",
    "fine",
    "wow",
    "huh",
    "really",
    "true",
    "mad",
    "bad",
    "good",
    "clean",
    "crazyyy",
    "yo",
    "man",
    "girl",
    "brother"
]

marked_words = set()

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global marked_words

    if message.author.bot:
        return

    content = message.content.lower()

    for word in BINGO_WORDS:
        if word in content and word not in marked_words:
            marked_words.add(word)
            await message.channel.send(f"✅ Word marked: {word}")

    if len(marked_words) >= 36:
        await message.channel.send("🎉 BINGO BLACKOUT COMPLETE! 🎉")
        marked_words.clear()

    await bot.process_commands(message)

# =========================
# START BOT
# =========================

keep_alive()
bot.run(TOKEN)
