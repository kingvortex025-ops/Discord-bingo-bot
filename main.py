import discord
from discord.ext import commands
from discord import app_commands
import os
import random
from flask import Flask
from threading import Thread

# =========================
# KEEP RENDER ALIVE
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
# BOT SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("TOKEN not found!")
    exit(1)

# =========================
# SETTINGS
# =========================

GRID_SIZE = 6
STICKER_TRIGGER_ID = 1476206893495095449
BINGO_CHANNEL_NAME = "bingo"

BINGO_WORDS = [
    "diddy","epstein","sus","crazy","wild","lol",
    "bruh","nah","what","real","fake","insane",
    "bro","why","no way","stop","wait","serious",
    "joke","cap","facts","ok","fine","wow",
    "huh","really","true","mad","bad","good",
    "clean","yo","man","girl","brother","crazyyy",
    "crazyyy2","random","fire","lowkey","highkey",
    "fr","ong","mid","clutch","goat","rip",
    "yuta slander","give me mod","i want mod",
    "fuck","die","bum","pedophile","im goated"
]

board_words = random.sample(BINGO_WORDS, GRID_SIZE * GRID_SIZE)
marked_words = set()

# =========================
# BOARD GENERATOR
# =========================

def generate_board():
    board_text = ""
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            word = board_words[i * GRID_SIZE + j]
            if word in marked_words:
                board_text += "🟩 "
            else:
                board_text += "🟥 "
        board_text += "\n"
    return board_text

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(e)

    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global marked_words

    if message.author.bot:
        return

    # Only allow in #bingo channel
    if message.channel.name != BINGO_CHANNEL_NAME:
        return

    content = message.content.lower()

    # Word trigger
    for word in board_words:
        if word in content:
            marked_words.add(word)

    # Sticker trigger
    if message.stickers:
        for sticker in message.stickers:
            if sticker.id == STICKER_TRIGGER_ID:
                random_word = random.choice(board_words)
                marked_words.add(random_word)
                await message.channel.send("🎯 Sticker triggered a random mark!")

    # Check blackout win
    if len(marked_words) >= GRID_SIZE * GRID_SIZE:
        await message.channel.send("🎉 BINGO BLACKOUT COMPLETE! 🎉")
        marked_words.clear()

    await bot.process_commands(message)

# =========================
# PREFIX COMMAND
# =========================

@bot.command()
async def ping(ctx):
    if ctx.channel.name != BINGO_CHANNEL_NAME:
        return
    await ctx.send("🏓 Pong!")

# =========================
# SLASH COMMANDS
# =========================

@bot.tree.command(name="board", description="Show current bingo board")
async def board(interaction: discord.Interaction):
    if interaction.channel.name != BINGO_CHANNEL_NAME:
        await interaction.response.send_message(
            "❌ This command can only be used in #bingo channel.",
            ephemeral=True
        )
        return
    await interaction.response.send_message(generate_board())

@bot.tree.command(name="reset", description="Reset the bingo board")
async def reset(interaction: discord.Interaction):
    global board_words, marked_words

    if interaction.channel.name != BINGO_CHANNEL_NAME:
        await interaction.response.send_message(
            "❌ This command can only be used in #bingo channel.",
            ephemeral=True
        )
        return

    board_words = random.sample(BINGO_WORDS, GRID_SIZE * GRID_SIZE)
    marked_words.clear()
    await interaction.response.send_message("🔄 Bingo board reset!")

# =========================
# START
# =========================

keep_alive()
bot.run(TOKEN)
