import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import asyncio
from database.db import connect_to_db, get_db

async def convert_reputation_to_power():
    await connect_to_db()
    db = get_db()
    await db.users.update_many(
        {"reputation": {"$exists": True}},
        [{"$set": {"power": "$reputation"}}, {"$unset": "reputation"}]
    )
    print("✅ Todos os usuários atualizados: 'reputation' → 'power'.")

asyncio.run(convert_reputation_to_power())
