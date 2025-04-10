import discord
from discord.ext import commands
import os
from database.db import connect_to_db
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    await connect_to_db()

    from database.db import get_db
    db = get_db()
    collection = db["characters"]
    total = await collection.count_documents({})

    if total == 0:
        print("📥 Coleção 'personagens' vazia. Inserindo dados do JSON...")
        from database.insert_data import insert_characters
        await insert_characters()
    else:
        print(f"📦 Coleção 'personagens' já contém {total} documentos.")

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.register")
    await bot.load_extension("cogs.profile")
    await bot.load_extension("cogs.daily")
    await bot.load_extension("cogs.rewards")
    await bot.load_extension("cogs.work")
    await bot.load_extension("cogs.help")
    await bot.load_extension("cogs.character_list")
    await bot.load_extension("cogs.powerboard")
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.rolls")
  

bot.run(os.getenv("DISCORD_TOKEN"))
