import discord
from discord.ext import commands
from database.db import get_db
from utils.power import check_rank_promotion, calculate_total_power
from utils.stars_system import StarsSystem
from services.collection_service import add_to_collection
import random
from datetime import datetime
import pytz
from typing import List, Dict

OWNER_ID = 1151268641401221241

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone("America/Sao_Paulo")  # Adicionando o timezone

    @commands.command(name="clearcollection")
    @is_owner()
    async def limpar_colecao(self, ctx, member: discord.Member = None):
        """Limpa a coleção de um usuário (ou sua própria)"""
        member = member or ctx.author
        db = get_db()
        user_id = str(member.id)

        await db["users"].update_one(
            {"_id": user_id},
            {"$set": {"collection": []}}
        )

        updated_user = await db["users"].find_one({"_id": user_id})
        new_power = calculate_total_power(updated_user.get("collection", []))

        await db["users"].update_one(
            {"_id": user_id},
            {"$set": {"power": new_power}}
        )

        await check_rank_promotion(self.bot, int(user_id), updated_user.get("power", 0), new_power, ctx.channel)

        await ctx.send(f"🧹 Coleção de {member.display_name} foi limpa com sucesso!")

    @commands.command(name="addcoins")
    @is_owner()
    async def add_coins(self, ctx, member: discord.Member, quantidade: int):
        """Adiciona moedas a um usuário"""
        db = get_db()
        user_id = str(member.id)

        await db["users"].update_one(
            {"_id": user_id},
            {"$inc": {"coins": quantidade}}
        )

        await ctx.send(f"💰 {quantidade} moedas adicionadas para {member.display_name}.")
    
    @commands.command(name="removecoins")
    @is_owner()
    async def remove_coins(self, ctx, member: discord.Member):
        """Zera as moedas de um usuário"""
        db = get_db()
        user_id = str(member.id)

        await db["users"].update_one(
            {"_id": user_id},
            {"$set": {"coins": 0}}
        )

        await ctx.send(f"💸 As moedas de {member.display_name} foram zeradas!")
    
    @commands.command(name="resetrolls")
    @is_owner()
    async def reset_rolls(self, ctx, member: discord.Member = None):
        """Reseta o histórico de rolls de um usuário"""
        member = member or ctx.author
        db = get_db()
        user_id = str(member.id)

        await db["users"].update_one(
            {"_id": user_id},
            {"$set": {"roll_history": []}}
        )

        updated_user = await db["users"].find_one({"_id": user_id})
        rolls_left = 10 - len(updated_user.get("roll_history", []))

        await ctx.send(f"🔄 O histórico de rolls de {member.display_name} foi resetado com sucesso! Rolls restantes: {rolls_left}.")

    @commands.command(name="adminroll", aliases=["aroll"])
    @is_owner()
    async def admin_roll(self, ctx, quantidade: int):
        """
        [ADMIN] Rola uma quantidade específica de personagens sem cooldown
        Uso: !adminroll <quantidade>
        """
        if quantidade < 1 or quantidade > 100:
            return await ctx.send("❌ Quantidade deve ser entre 1 e 100")

        db = get_db()
        user_id = str(ctx.author.id)
        star_system = StarsSystem(user_id)
        
        try:
            user_data = await db["users"].find_one({"_id": user_id})
            if not user_data:
                return await ctx.send("❌ Usuário não registrado")

            collection = user_data.get("collection", [])
            old_power = calculate_total_power(collection)
            characters = await self._get_roll_characters(quantidade)
            new_chars_info = []

            for char in characters:
                char_id = str(char["_id"])
                existing_char_index = next((i for i, c in enumerate(collection) if str(c.get("_id")) == char_id), None)
                
                if existing_char_index is not None:
                    # Atualiza as estrelas no personagem existente
                    collection[existing_char_index]['stars'] = min(collection[existing_char_index].get('stars', 0) + 1, 20)
                    stars = collection[existing_char_index]['stars']
                    action = f"🌟 +1 Estrela (Total: {stars})"
                else:
                    # Adiciona novo personagem com 0 estrelas
                    new_char = char.copy()
                    new_char['stars'] = 0
                    collection.append(new_char)
                    stars = 0
                    action = "🎉 Novo personagem!"
                
                new_chars_info.append({
                    "char": char,
                    "action": action,
                    "stars": stars
                })

            # Atualiza a coleção completa no banco de dados
            await db["users"].update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "collection": collection,
                        "last_roll": datetime.now(self.timezone).isoformat()
                    }
                }
            )

            await self._send_roll_results(ctx, new_chars_info, star_system)
            
            new_power = calculate_total_power(collection)
            await check_rank_promotion(self.bot, user_id, old_power, new_power, ctx.channel)

        except Exception as e:
            print(f"Erro no admin_roll: {e}")
            await ctx.send("❌ Ocorreu um erro ao processar o roll administrativo")

    async def _get_roll_characters(self, quantity: int) -> List[Dict]:
        """Gera os personagens aleatórios para o roll"""
        db = get_db()
        characters = []
        
        for _ in range(quantity):
            rarity = self._get_random_rarity()
            char = await self._get_random_character(rarity)
            if char:
                characters.append(char)
        
        return characters

    async def _send_roll_results(self, ctx, characters_info: List[Dict], star_system: StarsSystem):
        """Envia os resultados do roll em uma única embed organizada"""
        embed = discord.Embed(
            title=f"🎉 {ctx.author.display_name} obteve {len(characters_info)} personagens!",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        # Agrupa por raridade
        rarity_order = ["legendary", "epic", "rare", "uncommon", "common"]
        grouped_chars = {rarity: [] for rarity in rarity_order}
        
        for char_info in characters_info:
            grouped_chars[char_info["char"]["rarity"]].append(char_info)
        
        # Adiciona cada grupo à embed
        for rarity in rarity_order:
            if not grouped_chars[rarity]:
                continue
                
            rarity_name = rarity.capitalize()
            emoji = self._get_rarity_emoji(rarity)
            value_text = []
            
            for char_info in grouped_chars[rarity]:
                char = char_info["char"]
                stars = star_system.get_star_display(char_info['stars'])
                value_text.append(
                    f"{emoji} **{char['name']}** - "
                    f"{char_info['action']} {stars}"
                )
            
            embed.add_field(
                name=f"{emoji} {rarity_name} ({len(grouped_chars[rarity])})",
                value="\n".join(value_text),
                inline=False
            )
        
        embed.set_footer(text=f"Roll administrativo em {datetime.now(self.timezone).strftime('%d/%m às %H:%M')}")
        await ctx.send(embed=embed)

    def _get_rarity_emoji(self, rarity: str) -> str:
        """Retorna emoji correspondente à raridade"""
        emojis = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟡"
        }
        return emojis.get(rarity, "")

    def _get_random_rarity(self):
        rand = random.random()
        cumulative = 0.0
        for rarity, prob in {
            "common": 0.47,
            "uncommon": 0.3375,
            "rare": 0.15,
            "epic": 0.04,
            "legendary": 0.0025
        }.items():
            cumulative += prob
            if rand <= cumulative:
                return rarity
        return "common"

    async def _get_random_character(self, rarity):
        db = get_db()
        chars = await db["characters"].find({"rarity": rarity}).to_list(None)
        return random.choice(chars) if chars else None

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))