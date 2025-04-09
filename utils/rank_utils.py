from utils.power import get_power_rank, POWER_TIERS
from database.db import get_db


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

def extract_rank_name(rank_str: str) -> str:
    """Pega apenas o nome do rank (sem emoji)"""
    return rank_str.split(" ", 1)[1] if " " in rank_str else rank_str

async def check_rank_promotion(bot, user_id: int, old_power: int, new_power: int, channel):
    old_rank = get_power_rank(old_power)
    new_rank = get_power_rank(new_power)

    if old_rank != new_rank:
        old_rank_name = extract_rank_name(old_rank)
        new_rank_name = extract_rank_name(new_rank)

        # Dar recompensa de coins
        reward = RANK_REWARDS.get(new_rank_name, 0)

        if reward > 0:
            db = get_db()
            await db["users"].update_one(
                {"_id": user_id},
                {"$inc": {"coins": reward}}
            )

        user = await bot.fetch_user(user_id)
        await channel.send(
            f"🎉 {user.mention} subiu de rank!\n"
            f"🔼 **{old_rank} ➜ {new_rank}**\n"
            f"💰 Recompensa: **{reward} coins**"
        )
