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

board_words = []
marked_words = set()
game_active = False

# =========================
# BOARD GENERATOR
# =========================

def generate_board():
    board_text = ""

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            word = board_words[i * GRID_SIZE + j]

            if word in marked_words:
                board_text += f"🟩 {word}\t"
            else:
                board_text += f"🟥 {word}\t"

        board_text += "\n\n"

    return board_text

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global marked_words

    if message.author.bot:
        return

    if not game_active:
        await bot.process_commands(message)
        return

    content = message.content.lower()

    # WORD TRIGGER (ALL CHANNELS)
    for word in board_words:
        if word in content and word not in marked_words:
            marked_words.add(word)
            await message.channel.send(f"✅ **{word}** marked on the board!")

    # STICKER TRIGGER (ALL CHANNELS)
    if message.stickers:
        for sticker in message.stickers:
            if sticker.id == STICKER_TRIGGER_ID:
                random_word = random.choice(board_words)
                if random_word not in marked_words:
                    marked_words.add(random_word)
                    await message.channel.send(f"🎯 Sticker marked **{random_word}**!")

    # BLACKOUT WIN (announce in #bingo)
    if game_active and len(marked_words) >= GRID_SIZE * GRID_SIZE:
        for channel in message.guild.channels:
            if channel.name == BINGO_CHANNEL_NAME:
                await channel.send("🎉 BINGO BLACKOUT COMPLETE! 🎉")
                break
        marked_words.clear()

    await bot.process_commands(message)

# =========================
# PREFIX COMMAND
# =========================

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# =========================
# SLASH COMMANDS (BINGO ONLY)
# =========================

@bot.tree.command(name="start", description="Start a new bingo game")
async def start(interaction: discord.Interaction):
    global board_words, marked_words, game_active

    if interaction.channel.name != BINGO_CHANNEL_NAME:
        await interaction.response.send_message(
            "❌ Use this in #bingo channel only.",
            ephemeral=True
        )
        return

    board_words = random.sample(BINGO_WORDS, GRID_SIZE * GRID_SIZE)
    marked_words.clear()
    game_active = True

    await interaction.response.send_message("🎮 Bingo game started!")

@bot.tree.command(name="board", description="Show current bingo board")
async def board(interaction: discord.Interaction):
    if interaction.channel.name != BINGO_CHANNEL_NAME:
        await interaction.response.send_message(
            "❌ Use this in #bingo channel only.",
            ephemeral=True
        )
        return

    if not game_active:
        await interaction.response.send_message(
            "❌ No active bingo game. Use /start first."
        )
        return

    await interaction.response.send_message(generate_board())

@bot.tree.command(name="reset", description="Reset the bingo board")
async def reset(interaction: discord.Interaction):
    global board_words, marked_words

    if interaction.channel.name != BINGO_CHANNEL_NAME:
        await interaction.response.send_message(
            "❌ Use this in #bingo channel only.",
            ephemeral=True
        )
        return

    if not game_active:
        await interaction.response.send_message(
            "❌ No active game to reset."
        )
        return

    board_words = random.sample(BINGO_WORDS, GRID_SIZE * GRID_SIZE)
    marked_words.clear()

    await interaction.response.send_message("🔄 Bingo board reset!")

# =========================
# START BOT
# =========================

keep_alive()
bot.run(TOKEN)
