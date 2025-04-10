from database.db import get_db
from time import sleep

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

DAILY_REWARDS = {
    "Iniciante": 400,
    "Aventureiro": 600,
    "Guerreiro": 800,
    "Herói": 1000,
    "Elite": 1400,
    "Mítico": 2000,
    "Lendário": 3000,
    "Divino": 4500,
    "Celestial": 6000,
    "Supremo": 8500,
}

def get_power_rank(power: int) -> str:
    for tier in POWER_TIERS:
        if power >= tier["min"]:
            return f"{tier['emoji']} {tier['name']}"
    return "❓ Desconhecido"


def extract_rank_name(rank_str: str) -> str:
    """Pega apenas o nome do rank (sem emoji)."""
    return rank_str.split(" ", 1)[1] if " " in rank_str else rank_str


def calculate_total_power(collection: list) -> int:
    """Calcula o poder total de um jogador com bônus de estrelas."""
    total = 0
    for char in collection:
        base = char.get("power_base", 0)
        stars = char.get("stars", 0)
        bonus = 1 + stars * 0.1
        total += int(base * bonus)
    return total


async def check_rank_promotion(bot, user_id: int, old_power: int, new_power: int, channel):
    old_rank = get_power_rank(old_power)
    new_rank = get_power_rank(new_power)

    if old_rank != new_rank:
        new_rank_name = extract_rank_name(new_rank)

        if new_power > old_power:
            reward = RANK_REWARDS.get(new_rank_name, 0)
            sleep(1.8)
            message = f"🎉 <@{user_id}> subiu de rank!\n🔼 **{old_rank} ➜ {new_rank}**\n💰 Recompensa: **{reward} coins**"
        else:
            sleep(1.8)
            message = f"⚠️ <@{user_id}> foi rebaixado de rank.\n🔽 **{old_rank} ➜ {new_rank}**"

        if new_power > old_power:
            db = get_db()
            await db["users"].update_one(
                {"_id": str(user_id)},
                {"$inc": {"coins": reward}}
            )

        await channel.send(message)
