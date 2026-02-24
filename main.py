import discord
from discord import app_commands
import os
import re

# ====== TOKEN FROM RENDER ENVIRONMENT ======
TOKEN = os.environ["TOKEN"]

# ====== INTENTS ======
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ====== BINGO WORDS ======
BINGO_WORDS = [
    "diddy","epstin","gay","fuck","goon","dick",
    "wanna play jjs","i want to be mod","can i be mod",
    "give me mod","gimme mod","mono","yuta slander",
    "pets","israel","netanyahu","bum","1v1","yuta fraud!",
    "isreal","emoji_50","emoji_51","ilachie","i3gabe",
    "i3puck","ileren","i3mono","ilcosmo","i3jeff",
    "ilangel","iljuls","ilnaoya","ilnoemi",
    "ilcryptt","ic","im goated"
]

# ====== SERVER STORAGE ======
guild_data = {}

def get_data(guild_id):
    if guild_id not in guild_data:
        guild_data[guild_id] = {
            "active": False,
            "marked": set()
        }
    return guild_data[guild_id]

# ====== BOT READY ======
@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

# ====== MESSAGE LISTENER ======
@client.event
async def on_message(message):
    if not message.guild:
        return

    if message.author.bot:
        return

    data = get_data(message.guild.id)

    if not data["active"]:
        return

    # Combine message content
    content = message.content.lower()

    # Add sticker names
    for sticker in message.stickers:
        content += " " + sticker.name.lower()

    # Add custom emoji names
    emoji_matches = re.findall(r"<a?:([a-zA-Z0-9_]+):\d+>", message.content)
    for emoji_name in emoji_matches:
        content += " " + emoji_name.lower()

    for word in BINGO_WORDS:
        if word in content and word not in data["marked"]:
            data["marked"].add(word)
            await message.channel.send(f"🎯 Marked: **{word}**")

            # BLACKOUT WIN
            if len(data["marked"]) == len(BINGO_WORDS):
                await message.channel.send(
                    f"🎉 {message.author.mention} COMPLETED BLACKOUT BINGO!!! 🎉\n"
                    "https://media.tenor.com/6gHLhmwO87sAAAAC/anime-celebration.gif"
                )
                data["active"] = False
            break

# ==============================
# SLASH COMMANDS (ONLY IN #bingo)
# ==============================

@tree.command(name="startgame", description="Start the bingo game")
async def startgame(interaction: discord.Interaction):
    if interaction.channel.name != "bingo":
        await interaction.response.send_message(
            "Use this command in #bingo channel.",
            ephemeral=True
        )
        return

    data = get_data(interaction.guild.id)
    data["active"] = True
    data["marked"] = set()

    await interaction.response.send_message(
        "🔥 Bingo game started! Fill all squares to win!"
    )

@tree.command(name="reset", description="Reset the bingo board")
async def reset(interaction: discord.Interaction):
    if interaction.channel.name != "bingo":
        await interaction.response.send_message(
            "Use this command in #bingo channel.",
            ephemeral=True
        )
        return

    data = get_data(interaction.guild.id)
    data["active"] = False
    data["marked"] = set()

    await interaction.response.send_message("♻️ Bingo board reset.")

@tree.command(name="board", description="Show bingo progress")
async def board(interaction: discord.Interaction):
    if interaction.channel.name != "bingo":
        await interaction.response.send_message(
            "Use this command in #bingo channel.",
            ephemeral=True
        )
        return

    data = get_data(interaction.guild.id)

    total = len(BINGO_WORDS)
    marked = len(data["marked"])
    percent = int((marked / total) * 100)

    await interaction.response.send_message(
        f"🎯 BLACKOUT PROGRESS\n\n"
        f"Marked: {marked}/{total}\n"
        f"Remaining: {total - marked}\n"
        f"Progress: {percent}%"
    )

# ====== RUN BOT ======
client.run(TOKEN)
