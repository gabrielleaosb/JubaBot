from datetime import datetime, timedelta
import pytz
import random
import discord
from discord.ext import commands
from typing import List, Dict
from database.db import get_db
from utils.stars_system import StarsSystem
from utils.power import check_rank_promotion, calculate_total_power
from services.collection_service import add_to_collection
import asyncio
from utils.power import POWER_TIERS, RANK_REWARDS


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
        self.ROLL_COOLDOWN = timedelta(hours=1)
        self.CHARACTERS_PER_ROLL = 10

    @commands.command(name="roll", aliases=["r"])
    async def roll(self, ctx):
        """Realiza um roll que retorna 10 personagens de uma vez (cooldown de 1 hora)"""
        if hasattr(ctx, '_roll_processed'):
            return
        ctx._roll_processed = True

        user_id = str(ctx.author.id)
        db = get_db()
        star_system = StarsSystem(user_id)

        try:
            user_data = await db["users"].find_one({"_id": user_id})
            if not user_data:
                return await ctx.send(f"{ctx.author.mention}, registre-se primeiro com `!register`!")

            now = datetime.now(self.timezone)
            last_roll = user_data.get("last_roll")
            
            if last_roll:
                last_roll_time = datetime.fromisoformat(last_roll)
                next_available = last_roll_time + self.ROLL_COOLDOWN
                if now < next_available:
                    time_left = next_available - now
                    return await ctx.send(
                        f"⏳ {ctx.author.mention}, você já usou seu roll hoje! "
                        f"Próximo roll disponível em {self._format_timedelta(time_left)}"
                    )

            characters = await self._get_roll_characters()
            
            collection = user_data.get("collection", [])
            old_power = calculate_total_power(collection)
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
                        "last_roll": now.isoformat()
                    }
                }
            )

            await self._send_roll_results(ctx, new_chars_info, star_system)
            
            new_power = calculate_total_power(collection)
            await check_rank_promotion(self.bot, user_id, old_power, new_power, ctx.channel)

        except Exception as e:
            print(f"Erro no comando roll: {e}")
            await ctx.send("❌ Ocorreu um erro ao processar seu roll. Tente novamente.")

    async def _get_roll_characters(self) -> List[Dict]:
        """Gera os 10 personagens aleatórios para o roll"""
        db = get_db()
        characters = []
        
        for _ in range(self.CHARACTERS_PER_ROLL):
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
        
        # Agrupa os personagens por raridade para organização
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
        
        embed.set_footer(text=f"Roll realizado em {datetime.now(self.timezone).strftime('%d/%m às %H:%M')}")
        await ctx.send(embed=embed)

    def _create_character_embed(self, char_info: Dict, index: int, star_system: StarsSystem) -> discord.Embed:
        """Cria um embed estilizado para cada personagem"""
        character = char_info["char"]
        rarity_colors = {
            "common": discord.Color.light_grey(),
            "uncommon": discord.Color.green(),
            "rare": discord.Color.blue(),
            "epic": discord.Color.purple(),
            "legendary": discord.Color.gold()
        }
        
        embed = discord.Embed(
            title=f"{index}. {character['name']}",
            description=(
                f"**Raridade:** {character['rarity'].capitalize()} {self._get_rarity_emoji(character['rarity'])}\n"
                f"**Tipo:** {character.get('type', 'hero').capitalize()}\n"
                f"**Ação:** {char_info['action']}\n"
                f"**Estrelas:** {star_system.get_star_display(char_info['stars'])}\n"
                f"**Poder Base:** {character.get('power_base', 100)}"
            ),
            color=rarity_colors.get(character['rarity'], discord.Color.default())
        )
        
        if character.get("description"):
            embed.add_field(name="Descrição", value=character["description"], inline=False)
        
        if character.get("image"):
            embed.set_image(url=character["image"])
        
        embed.set_footer(text=f"Roll de {datetime.now().strftime('%d/%m %H:%M')}")
        return embed

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

    def _format_timedelta(self, td: timedelta) -> str:
        """Formata timedelta para string legível"""
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

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