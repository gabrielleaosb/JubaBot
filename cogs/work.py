import discord
import random
from discord.ext import commands
from datetime import datetime, timedelta
import pytz
from database.db import get_db

class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone("America/Sao_Paulo")

    @commands.command(name="work")
    async def work(self, ctx):
        db = get_db()
        user_id = str(ctx.author.id)
        now = datetime.now(self.timezone)

        user_data = await db.users.find_one({"_id": user_id})

        if not user_data:
            await ctx.send(f"{ctx.author.mention}, você ainda não está registrado. Use `!register`.")
            return

        last_work_time = user_data.get("last_work_time")
        if last_work_time:
            if isinstance(last_work_time, str):
                last_work_time = datetime.fromisoformat(last_work_time)

            cooldown = timedelta(hours=1)
            if now - last_work_time < cooldown:
                remaining_time = cooldown - (now - last_work_time)
                hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
                minutes = remainder // 60
                await ctx.send(f"⏳ {ctx.author.mention}, você já trabalhou recentemente. Tente novamente em **{hours}h {minutes}min**.")
                return

        common_jobs = [
            ("Patrulhamento Noturno", "Você patrulhou as ruas e impediu pequenos crimes.", random.randint(80, 120)),
            ("Laboratório Tecnológico", "Você testou um novo traje.", random.randint(75, 105)),
            ("Infiltração Disfarçada", "Você se infiltrou em um esconderijo de vilões.", random.randint(80, 110)),
            ("Espionagem Básica", "Você espionou uma gangue local.", random.randint(75, 120)),
            ("Proteção em Evento", "Você protegeu um evento importante!", random.randint(85, 125)),
        ]

        uncommon_jobs = [
            ("Missão Intergaláctica", "Você desativou uma bomba alienígena!", random.randint(140, 185)),
            ("Roubo à Alta Tecnologia", "Você roubou equipamento avançado!", random.randint(135, 170)),
            ("Caçada de Vilão", "Você capturou um vilão procurado!", random.randint(140, 190)),
            ("Missão Mercenária", "Você cumpriu um contrato sombrio...", random.randint(135, 175)),
        ]

        rare_jobs = [
            ("Duelo Lendário", "Você derrotou um vilão épico!", random.randint(190, 285)),
            ("Ataque ao Quartel", "Você invadiu uma base de heróis!", random.randint(200, 290)),
            ("Salvou o Multiverso", "Você impediu o colapso do multiverso!", random.randint(200, 300)),
        ]

        epic_jobs = [
            ("Guerra Temporal", "Você lutou no passado e no futuro ao mesmo tempo!", random.randint(320, 480)),
            ("Aliança Sombria", "Você liderou uma equipe de vilões em uma missão de risco!", random.randint(310, 490)),
            ("Resgate Dimensional", "Você resgatou reféns de uma dimensão paralela!", random.randint(340, 500)),
        ]

        legendary_jobs = [
            ("Combate Cósmico Final", "Você enfrentou uma entidade cósmica para salvar a existência!", random.randint(800, 1200)),
            ("Ascensão do Herói Supremo", "Você foi reconhecido como o maior herói do século!", random.randint(800, 1200)),
            ("Domínio do Multiverso", "Você tomou controle de realidades paralelas inteiras!", random.randint(800, 1200)),
        ]

        job_pool = [
            (common_jobs, 40, "Comum", "🟢", discord.Color.green()),
            (uncommon_jobs, 25, "Incomum", "🔵", discord.Color.blue()),
            (rare_jobs, 20, "Raro", "🟣", discord.Color.purple()),
            (epic_jobs, 10, "Épico", "🟠", discord.Color.orange()),
            (legendary_jobs, 5, "Lendário", "🔴", discord.Color.red()),
        ]

        job_list, _, rarity_name, rarity_emoji, embed_color = random.choices(
            job_pool,
            weights=[j[1] for j in job_pool],
            k=1
        )[0]
        job = random.choice(job_list)
        title, description, reward = job

        await db.users.update_one(
            {"_id": user_id},
            {
                "$inc": {"coins": reward},
                "$set": {"last_work_time": now.isoformat()}
            }
        )

        embed = discord.Embed(
            title=f"{rarity_emoji} {title}",
            description=description,
            color=embed_color
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.add_field(name="🏆 Recompensa", value=f"💰 {reward} moedas", inline=True)
        embed.add_field(name="⭐ Raridade", value=f"{rarity_emoji} {rarity_name}", inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Work(bot))
