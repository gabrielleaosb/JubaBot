POWER_TIERS = [
    {"min": 10000, "name": "Supremo", "emoji": "👑"},
    {"min": 7000, "name": "Celestial", "emoji": "🌌"},
    {"min": 5500, "name": "Divino", "emoji": "🌟"},
    {"min": 4000, "name": "Lendário", "emoji": "🔥"},
    {"min": 2500, "name": "Mítico", "emoji": "⚡"},
    {"min": 1500, "name": "Elite", "emoji": "🛡️"},
    {"min": 1000, "name": "Herói", "emoji": "⚔️"},
    {"min": 500, "name": "Guerreiro", "emoji": "🎯"},
    {"min": 200,  "name": "Aventureiro", "emoji": "🏹"},
    {"min": 0,   "name": "Iniciante", "emoji": "🐣"},
]

def get_power_rank(power: int) -> str:
    for tier in POWER_TIERS:
        if power >= tier["min"]:
            return f"{tier['emoji']} {tier['name']}"
    return "❓ Desconhecido"

