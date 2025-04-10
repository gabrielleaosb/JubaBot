from datetime import datetime, timedelta
import pytz
import random
import discord
from discord.ext import commands
from database.db import get_db
from utils.stars_system import StarsSystem
from utils.power import check_rank_promotion


POWER_TIERS = [
    {"min": 20000, "name": "Supremo", "emoji": "👑"},
    {"min": 15000, "name": "Celestial", "emoji": "🌌"},
    {"min": 10000, "name": "Divino", "emoji": "🌟"},
    {"min": 8000, "name": "Lendário", "emoji": "🔥"},
    {"min": 6000, "name": "Mítico", "emoji": "⚡"},
    {"min": 4000, "name": "Elite", "emoji": "🛡️"},
    {"min": 2500, "name": "Herói", "emoji": "⚔️"},
    {"min": 1000, "name": "Guerreiro", "emoji": "🎯"},
    {"min": 500,  "name": "Aventureiro", "emoji": "🏹"},
    {"min": 0,   "name": "Iniciante", "emoji": "🐣"},
]

RANK_REWARDS = {
    "Iniciante": 0,
    "Aventureiro": 200,
    "Guerreiro": 400,
    "Herói": 800,
    "Elite": 1500,
    "Mítico": 2800,
    "Lendário": 5000,
    "Divino": 7500,
    "Celestial": 10000,
    "Supremo": 15000,
}

def get_power_rank(power: int) -> str:
    for tier in POWER_TIERS:
        if power >= tier["min"]:
            return f"{tier['emoji']} {tier['name']}"
    return "❓ Desconhecido"


def calculate_total_power(collection: list) -> int:
    """Calcula o poder total de um jogador com bônus de estrelas."""
    total = 0
    for char in collection:
        base = char.get("power_base", 0)
        stars = char.get("stars", 0)
        bonus = 1 + stars * 0.1
        total += int(base * bonus)
    return total


class Rolls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone("America/Sao_Paulo")
        self.RARITY_PROBABILITIES = {
            "common": 0.47,
            "uncommon": 0.3375,
            "rare": 0.15,
            "epic": 0.04,
            "legendary": 0.0025
        }

    @commands.command(name="roll", aliases=["r"])
    async def roll(self, ctx):
        # Verificar se a mensagem já foi processada
        if hasattr(ctx, '_roll_processed'):
            return
        ctx._roll_processed = True

        user_id = str(ctx.author.id)
        db = get_db()
        star_system = StarsSystem(user_id)

        try:
            # Verifica registro do usuário
            user_data = await db["users"].find_one({"_id": user_id})
            if not user_data:
                await ctx.send(f"{ctx.author.mention}, registre-se primeiro com `!register`!")
                return

            now = datetime.now(self.timezone)
            current_hour = now.replace(minute=0, second=0, microsecond=0)

            # Verifica o reset horário
            roll_history = user_data.get("roll_history", [])
            
            # Se há rolls no histórico, verifica se são da hora atual
            if roll_history:
                first_roll_time = datetime.fromtimestamp(roll_history[0], tz=self.timezone)
                first_roll_hour = first_roll_time.replace(minute=0, second=0, microsecond=0)
                
                if current_hour > first_roll_hour:
                    roll_history = []
                    await db["users"].update_one(
                        {"_id": user_id},
                        {"$set": {"roll_history": roll_history}}
                    )

            roll_limit = 10

            if len(roll_history) >= roll_limit:
                next_reset = current_hour + timedelta(hours=1)
                time_until_reset = next_reset - now
                minutes = int(time_until_reset.total_seconds() // 60)
                seconds = int(time_until_reset.total_seconds() % 60)
                
                await ctx.send(
                    f"{ctx.author.mention}, você já usou todas suas rolls nesta hora! "
                    f"Próximo reset em: {minutes}m {seconds}s"
                )
                return

            # Processar o roll
            rarity = self._get_random_rarity()
            char = await self._get_random_character(rarity)
            if not char:
                await ctx.send("Não foi possível encontrar um personagem para esta rolagem.")
                return

            # Registrar o novo roll
            roll_history.append(now.timestamp())
            await db["users"].update_one(
                {"_id": user_id},
                {"$set": {"roll_history": roll_history}}
            )

            # Atualizar coleção
            collection = user_data.get("collection", [])
            existing_char = next(
                (c for c in collection if str(c["_id"]) == str(char["_id"])), 
                None
            )

            old_power = calculate_total_power(collection)

            if existing_char:
                existing_char['stars'] = min(existing_char.get('stars', 0) + 1, 20)
                stars = existing_char['stars']
                action = f"🌟 +1 Estrela (Total: {stars})"
            else:
                new_character = {
                    "_id": char["_id"],
                    "name": char["name"],
                    "rarity": char["rarity"],
                    "power_base": char.get("power_base", 100),
                    "stars": 0,
                    "description": char.get("description", ""),
                    "image": char.get("image", "")
                }
                collection.append(new_character)
                stars = 0
                action = "🎉 Novo personagem!"

            await db["users"].update_one(
                {"_id": user_id},
                {"$set": {"collection": collection}}
            )

            # Criar embed
            embed = discord.Embed(
                title=f"{char['name']} ({rarity.capitalize()})",
                color=discord.Color.random()
            )
            embed.add_field(name="Ação", value=action, inline=True)
            embed.add_field(name="Estrelas", value=star_system.get_star_display(stars), inline=True)
            
            if char.get('image'):
                embed.set_image(url=char['image'])
                
            embed.set_footer(
                text=f"Rolls restantes: {10 - len(roll_history)}/10 | "
                    f"Próximo reset: {current_hour.hour + 1}:00"
            )

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Erro no comando roll: {e}")
            await ctx.send("Ocorreu um erro ao processar seu roll. Tente novamente.")

    def _get_random_rarity(self):
        rand = random.random()
        cumulative = 0.0
        for rarity, prob in self.RARITY_PROBABILITIES.items():
            cumulative += prob
            if rand <= cumulative:
                return rarity
        return "common"

    async def _get_random_character(self, rarity):
        db = get_db()
        chars = await db["characters"].find({"rarity": rarity}).to_list(None)
        return random.choice(chars) if chars else None

async def setup(bot):
    await bot.add_cog(Rolls(bot))
