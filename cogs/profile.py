import discord
from discord.ext import commands
from database.db import get_db

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx, member: discord.Member = None):
        db = get_db()
        target = member or ctx.author
        user_id = str(target.id)

        player = await db.users.find_one({"_id": user_id})

        if not player:
            if member:
                await ctx.send(f"{ctx.author.mention}, o usuário {target.mention} não está registrado!")
            else:
                await ctx.send(f"{ctx.author.mention}, você ainda não está registrado! Use `!register` primeiro.")
            return

        embed = discord.Embed(
            title=f"📜 Perfil de {target.name}",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=target.avatar.url if target.avatar else discord.Embed.Empty)
        embed.add_field(name="💰 Coins", value=player.get("coins", 0), inline=True)
        embed.add_field(name="⭐ Reputação", value=player.get("reputation", 0), inline=True)
        embed.add_field(name="🎴 Coleção", value=len(player.get("collection", [])), inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
