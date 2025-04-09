import discord
from discord.ext import commands
from database.db import get_db
from utils.power import get_power_rank, POWER_TIERS

class PowerBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="infopower", aliases=["ip"])
    async def info_power(self, ctx):
        embed = discord.Embed(
            title="🏆 Classificações de Poder",
            description="Confira os níveis e classificações com base no seu poder acumulado!",
            color=discord.Color.orange()
        )

        for tier in POWER_TIERS:
            embed.add_field(
                name=f"{tier['emoji']} {tier['name']}",
                value=f"`{tier['min']}+ Poder`",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="rank", aliases=["r"])
    async def rank(self, ctx):
        db = get_db()
        users = await db["users"].find().to_list(length=100)

        def calculate_power(user):
            collection = user.get("collection", [])
            return sum(int(char.get("power_base", 0) * (1 + char.get("stars", 0) * 0.1)) for char in collection)

        users.sort(key=calculate_power, reverse=True)


        if not users:
            return await ctx.send("❌ Nenhum jogador registrado ainda.")

        embed = discord.Embed(
            title="🏆 Ranking dos Mais Poderosos",
            color=discord.Color.dark_gold()
        )

        for i, user in enumerate(users[:10], start=1):
            name = user.get("name", "Desconhecido")
            power = calculate_power(user)
            rank = get_power_rank(power)
            embed.add_field(
                name=f"{i}. {name}",
                value=f"{rank} • `{power}` Poder",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PowerBoard(bot))
