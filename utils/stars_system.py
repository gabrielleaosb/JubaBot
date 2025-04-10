from database.db import get_db
from utils.star_emoji import get_star_display  

class StarsSystem:
    def __init__(self, user_id):
        self.db = get_db()
        self.user_id = user_id

    async def add_stars(self, character, collection):
        """
        Adiciona uma estrela ao personagem.
        - Personagem novo começa com 0 estrelas (☆)
        - Primeira cópia: 1 estrela (⭐) + 10% de power_base
        - Cópias subsequentes: +1 estrela (até 20)
        """
        existing_char = next(
            (c for c in collection if str(c["_id"]) == str(character["_id"])), 
            None
        )
        
        if not existing_char:
            return None 

        new_stars = min(existing_char.get('stars', 0) + 1, 20)
        
        base_power = character.get('power_base', 100) 
        new_power = base_power * (1 + 0.1 * new_stars)
        
        # Atualiza os valores
        existing_char['stars'] = new_stars
        existing_char['power'] = new_power

        await self.update_user_collection(collection)
        
        if new_stars >= 20:
            new_rarity = self.get_next_rarity(existing_char['rarity'])
            existing_char['rarity'] = new_rarity
            existing_char['stars'] = 1  
            return f"✨ {character['name']} evoluiu para {new_rarity.capitalize()}!"
        
        return f"⭐ {character['name']} agora tem {new_stars} estrelas (Poder: {new_power:.1f})"

    async def add_new_character(self, character, collection):
        """Adiciona novo personagem com 0 estrelas (sem bônus de poder)"""
        new_char = {
            "_id": character["_id"],
            "name": character["name"],
            "rarity": character["rarity"],
            "power_base": character.get("power_base", 100), 
            "power": character.get("power_base", 100),  
            "stars": 0, 
            "description": character.get("description", ""),
            "image": character.get("image", "")
        }
        collection.append(new_char)
        await self.update_user_collection(collection)
        return f"🎉 Novo personagem: {character['name']} (0 estrelas)"

    def get_next_rarity(self, current_rarity):
        rarity_order = ["common", "uncommon", "rare", "epic", "legendary"]
        try:
            return rarity_order[rarity_order.index(current_rarity) + 1]
        except IndexError:
            return current_rarity  

    async def update_user_collection(self, collection):
        await self.db.users.update_one(
            {"_id": self.user_id},
            {"$set": {"collection": collection}}
        )

    def get_star_display(self, stars: int) -> str:
        """Retorna emoji de estrelas: ☆ para 0, ⭐ para >=1"""
        return "☆" if stars == 0 else "⭐" * stars
