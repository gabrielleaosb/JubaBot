import discord
from discord.ext import commands
from discord.ui import View, Button
from database.db import get_db
from utils.power import get_power_rank


class ProfileView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎴 Ver Coleção", style=discord.ButtonStyle.primary, disabled=True)
    async def view_collection(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🚧 Esta funcionalidade ainda está em desenvolvimento!", ephemeral=True)

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile", aliases=["perfil", "p"])
    async def profile(self, ctx, member: discord.Member = None):
        db = get_db()
        target = member or ctx.author
        user_id = str(target.id)

        player = await db.users.find_one({"_id": user_id})

        if not player:
            msg = f"{ctx.author.mention}, o usuário {target.mention} não está registrado!" if member else f"{ctx.author.mention}, você ainda não está registrado! Use `!register` primeiro."
            return await ctx.send(msg)

        power = player.get("power", 0)
        rank = get_power_rank(power)

        embed = discord.Embed(
            title=f"📜 Perfil de {target.display_name}",
            color=discord.Color.gold()
        )

        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)

        embed.description = (
            f"**Moedas:** `{player.get('coins', 0)}`\n\n"
            f"⭐ **PODER TOTAL** ⭐\n"
            f"```{power}```"
            f"Rank:  {rank}"
        )

        view = ProfileView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Profile(bot))
