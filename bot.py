import discord
from discord.ext import commands
import os
from database.db import connect_to_db
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    await connect_to_db()

# Carregando os cogs
@bot.event
async def setup_hook():
    await bot.load_extension("cogs.register")
    await bot.load_extension("cogs.profile")
    await bot.load_extension("cogs.daily")
    await bot.load_extension("cogs.rewards")
    await bot.load_extension("cogs.work")
    await bot.load_extension("cogs.packview")

bot.run(os.getenv("DISCORD_TOKEN"))
