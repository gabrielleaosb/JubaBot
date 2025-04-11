import discord
from discord.ext import commands
from database.db import get_db
from utils.power import get_power_rank, POWER_TIERS, calculate_total_power_with_stars
from bson import ObjectId
from typing import Union, List, Dict

class PowerBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="infopower", aliases=["ip"])
    async def info_power(self, ctx):
        """Mostra informações sobre os níveis de poder"""
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

    async def get_character_power(self, char_data: Union[ObjectId, Dict], db) -> int:
        """Calcula o poder de um personagem, lidando com ObjectId ou documento completo"""
        if isinstance(char_data, ObjectId):
            # Se for apenas ObjectId, busca o personagem no banco
            char = await db["characters"].find_one({"_id": char_data})
            if not char:
                return 0
            power_base = char.get("power_base", 0)
            stars = 0  # Assume 0 estrelas se não houver informação
        else:
            # Se for documento completo
            power_base = char_data.get("power_base", 0)
            stars = char_data.get("stars", 0)
        
        return int(power_base * (1 + stars * 0.1))

    @commands.command(name="rank")
    async def rank(self, ctx):
        """Mostra o ranking baseado no poder total (base + estrelas)"""
        db = get_db()
        users = await db["users"].find().to_list(length=100)
        
        ranked_users = []
        for user in users:
            power = await calculate_total_power_with_stars(user["_id"])  # Usa a nova função
            ranked_users.append({
                "user": user,
                "power": power,
                "name": user.get("name", "Desconhecido")
            })
        
        ranked_users.sort(key=lambda x: x["power"], reverse=True)

        embed = discord.Embed(
            title="🏆 Ranking de Poder Total",
            description="Calculado com: (power_base × (1 + stars × 0.1))",
            color=discord.Color.gold()
        )

        for i, user_data in enumerate(ranked_users[:10], 1):
            embed.add_field(
                name=f"{i}. {user_data['name']}",
                value=f"{get_power_rank(user_data['power'])} • {user_data['power']} Poder",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PowerBoard(bot))