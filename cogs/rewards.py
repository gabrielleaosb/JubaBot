import discord
from discord.ext import commands
from database.db import get_db
from datetime import datetime, timedelta, time
import pytz

class Rewards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone("America/Sao_Paulo")

    @commands.command(name="rewards")
    async def rewards(self, ctx):
        db = get_db()
        user_id = str(ctx.author.id)
        now = datetime.now(self.timezone) 
        today = now.date()

        user = await db.users.find_one({"_id": user_id})
        if not user:
            await ctx.send(f"{ctx.author.mention}, você precisa se registrar primeiro com `!register`.")
            return

        # ---------------- DAILY ---------------- #
        last_daily_str = user.get("last_daily")
        daily_status = ""
        if last_daily_str:
            last_daily = datetime.strptime(last_daily_str, "%Y-%m-%d").date()
            if last_daily == today:
                # Calcula o horário de reset (meia-noite do próximo dia)
                reset_time = self.timezone.localize(datetime.combine(today + timedelta(days=1), time(0, 0)))
                remaining = reset_time - now
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes = remainder // 60
                daily_status = f"Já resgatado hoje.\nReseta em **{hours}h {minutes}min**."
            else:
                daily_status = "Disponível agora! Use `!daily`"
        else:
            daily_status = "Disponível agora! Use `!daily`"

        # ---------------- WORK ---------------- #
        last_work_str = user.get("last_work_time")  
        work_status = ""
        if last_work_str:
            if isinstance(last_work_str, str):
                last_work = datetime.fromisoformat(last_work_str)
            else:
                last_work = last_work_str

            cooldown = timedelta(hours=1)
            elapsed = now - last_work
            if elapsed < cooldown:
                remaining = cooldown - elapsed
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes = remainder // 60
                work_status = f"⏳ Já trabalhou recentemente.\nDisponível em **{hours}h {minutes}min**."
            else:
                work_status = "Disponível agora! Use !work"
        else:
            work_status = "Disponível agora! Use !work"

        # ---------------- ROLLS ---------------- #
        last_roll_str = user.get("last_roll")
        rolls_status = ""
        
        if last_roll_str:
            last_roll = datetime.fromisoformat(last_roll_str)
            
            if last_roll.tzinfo is None:
                last_roll = self.timezone.localize(last_roll)
            
            next_available = last_roll + timedelta(hours=1)
            
            if now < next_available:
                time_left = next_available - now
                hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                minutes = remainder // 60
                rolls_status = f"⏳ Roll já utilizado. Próximo disponível em **{hours}h {minutes}min**"
            else:
                rolls_status = "Disponível agora! Use `!roll`"
        else:
            rolls_status = "Disponível agora! Use `!roll`"

        # ---------------- EMBED ---------------- #
        embed = discord.Embed(
            title="🎁 Recompensas Diárias",
            description="Veja como ganhar moedas no jogo:",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

        embed.add_field(
            name="🗓️ `!daily`",
            value=daily_status,
            inline=False
        )

        embed.add_field(
            name="🛠️ `!work`",
            value=work_status,
            inline=False
        )

        embed.add_field(
            name="🎲 `!roll` (10 personagens)",
            value=rolls_status,
            inline=False
        )

        embed.set_footer(text="Mais formas de ganhar moedas em breve!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Rewards(bot))