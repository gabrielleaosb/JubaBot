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
        user_id = str(ctx.author.id)
        db = get_db()
        star_system = StarsSystem(user_id)

        # Verifica registro do usuário
        user_data = await db["users"].find_one({"_id": user_id})
        if not user_data:
            await ctx.send(f"{ctx.author.mention}, registre-se primeiro com `!register`!")
            return

        now = datetime.now(self.timezone)
        today = now.date()

        last_roll_str = user_data.get("last_roll")
        if last_roll_str:
            last_roll = datetime.strptime(last_roll_str, "%Y-%m-%d").date()
            if last_roll == today:
                await ctx.send(f"{ctx.author.mention}, você já usou seu roll hoje! Volte amanhã!")
                return
        
        next_reset = datetime.combine(today, datetime.min.time(), tzinfo=self.timezone) + timedelta(hours=now.hour + 1)
        
        if now >= next_reset:
            roll_history = []
            await db["users"].update_one(
                {"_id": user_id},
                {"$set": {"roll_history": roll_history}}
            )
            await ctx.send(f"{ctx.author.mention}, seu histórico de rolls foi resetado!")

        roll_history = user_data.get("roll_history", [])
        roll_limit = 10

        if len(roll_history) >= roll_limit:
            time_until_reset = next_reset - now
            hours = int(time_until_reset.total_seconds() // 3600)
            minutes = int((time_until_reset.total_seconds() % 3600) // 60)

            await ctx.send(
                f"{ctx.author.mention}, você já usou todas suas rolls! "
                f"Próximo reset em: {hours}h {minutes}m"
            )
            return

        roll_history.append(now.timestamp())
        await db["users"].update_one(
            {"_id": user_id},
            {
                "$set": {"last_roll": today.isoformat()},
                "$set": {"roll_history": roll_history}
            }
        )

        rarity = self._get_random_rarity()
        char = await self._get_random_character(rarity)

        if not char:
            await ctx.send("Não foi possível encontrar um personagem para esta rolagem.")
            return

        collection = user_data.get("collection", [])
        existing_char = next(
            (c for c in collection if str(c["_id"]) == str(char["_id"])), 
            None
        )

        rarity_colors = {
            "common": discord.Color.light_grey(),
            "uncommon": discord.Color.green(),
            "rare": discord.Color.blue(),
            "epic": discord.Color.purple(),
            "legendary": discord.Color.gold()
        }

        old_power = calculate_total_power(collection)

        if existing_char:
            existing_char['stars'] = min(existing_char.get('stars', 0) + 1, 20)
            base_power = existing_char.get('power_base', 100)
            existing_char['power'] = base_power * (1 + 0.1 * existing_char['stars'])
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

        new_power = calculate_total_power(collection)

        await check_rank_promotion(self.bot, user_id, old_power, new_power, ctx.channel)

        embed = discord.Embed(
            title=f"{char['name']} ({rarity.capitalize()})",
            description=char.get('rarity', 'Sem raridade.'),
            color=rarity_colors.get(char['rarity'], discord.Color.default())
        )

        embed.add_field(name="Ação", value=action, inline=True)
        embed.add_field(name="Estrelas", value=star_system.get_star_display(stars), inline=True)

        if 'image' in char and char['image']:
            embed.set_image(url=char['image'])

        embed.set_footer(
            text=f"Rolls restantes: {10 - len(roll_history)}/10 nesta hora | "
                f"Total na coleção: {len(collection)} personagens"
        )

        await ctx.send(embed=embed)

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
