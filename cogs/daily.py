import discord  # noqa: F401
from discord.ext import commands
from database.db import get_db
from datetime import datetime, timedelta
from utils.power import DAILY_REWARDS, get_power_rank, calculate_total_power
import pytz

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone("America/Sao_Paulo")

    @commands.command(name="daily")
    async def daily(self, ctx):
        db = get_db()
        user_id = str(ctx.author.id)
        now = datetime.now(self.timezone)
        today = now.date()

        user = await db.users.find_one({"_id": user_id})

        if not user:
            await ctx.send(f"{ctx.author.mention}, você ainda não está registrado! Use `!register` primeiro.")
            return

        last_daily_str = user.get("last_daily")
        if last_daily_str:
            last_daily = datetime.strptime(last_daily_str, "%Y-%m-%d").date()
            if last_daily == today:
                # Calcula o tempo restante até o próximo daily
                tomorrow = now + timedelta(days=1)
                reset_time = datetime.combine(tomorrow.date(), datetime.min.time()).astimezone(self.timezone)
                time_left = reset_time - now
                
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes = remainder // 60
                
                await ctx.send(
                    f"{ctx.author.mention}, você já resgatou seu prêmio diário hoje! "
                    f"Volte em **{hours}h {minutes}min**!"
                )
                return
        
        total_power = calculate_total_power(user.get("collection", []))
        player_rank = get_power_rank(total_power)
        rank_name = player_rank.split(" ", 1)[1]

        reward = DAILY_REWARDS.get(rank_name, 0)

        await db.users.update_one(
            {"_id": user_id},
            {
                "$inc": {"coins": reward},
                "$set": {"last_daily": today.isoformat()}
            }
        )

        await ctx.send(f"{ctx.author.mention}, você recebeu **{reward} moedas** hoje!  Volte amanhã pra mais!")

async def setup(bot):
    await bot.add_cog(Daily(bot))