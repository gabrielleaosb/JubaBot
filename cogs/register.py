import discord
from discord.ext import commands
from database.db import get_db

class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="register")
    async def register(self, ctx):
        db = get_db()
        user_id = str(ctx.author.id)

        player = await db.users.find_one({"_id": user_id})

        if player:
            if "inventory" not in player:
                await db.users.update_one({"_id": user_id}, {"$set": {"inventory": []}})
                await ctx.send(f"{ctx.author.mention}, seu inventário foi adicionado com sucesso! 🎉")
            else:
                await ctx.send(f"{ctx.author.mention}, você já está registrado!")
        else:
            new_player = {
                "_id": user_id,
                "name": ctx.author.name,
                "coins": 200,
                "collection": [],
                "inventory": [], 
                "power": 0
            }
            await db.users.insert_one(new_player)
            await ctx.send(f"{ctx.author.mention},  você foi registrado com sucesso com 200 moedas iniciais! ✅")


async def setup(bot):
    await bot.add_cog(Register(bot))
