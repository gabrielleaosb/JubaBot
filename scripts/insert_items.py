import asyncio
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import connect_to_db, get_db

async def insert_items():
    await connect_to_db()

    db = get_db()
    if db is None:
        print("Erro: Conexão com o banco de dados falhou!")
        return

    print("Banco de dados conectado com sucesso!")

    items = load_items()

    existing_items = await db["items"].find().to_list(length=100)

    if existing_items:
        print("Os itens já foram inseridos!")
        return

    for item in items:
        await db["items"].insert_one(item)

    print("Itens inseridos com sucesso!")

def load_items():
    with open("data/items.json", "r", encoding="utf-8") as file:
        return json.load(file)

asyncio.run(insert_items())
