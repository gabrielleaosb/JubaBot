from database.db import connect_to_db, get_db
import json

async def insert_characters():
    await connect_to_db()
    db_locale = get_db()
    collection = db_locale["characters"]

    with open("data/characters.json", "r", encoding="utf-8") as file:
        characters = json.load(file)

    json_names = [char["name"] for char in characters]

    await collection.delete_many({"name": {"$nin": json_names}})
    print("🗑️ Personagens removidos do banco que não estavam no JSON.")

    for character in characters:
        await collection.update_one(
            {"name": character["name"]},
            {"$set": character},
            upsert=True
        )

    print("✅ Banco sincronizado com characters.json com sucesso!")
