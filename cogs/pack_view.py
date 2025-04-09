import discord
from discord.ext import commands
from discord.ui import View, Button
from database.db import get_db
from utils.power import calculate_total_power, check_rank_promotion
import json
import random


RARITY_MAP = {
    "Comum": "common",
    "Incomum": "uncommon",
    "Raro": "rare",
    "Épico": "epic",
    "Lendário": "legendary"
}


class PackMenuView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Heróis", style=discord.ButtonStyle.secondary, custom_id="packs_hero")
    async def hero_packs(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self.bot.get_cog("PackView")
        if cog:
            await cog.show_packs_embed(interaction, "hero", 0, update=True)

    @discord.ui.button(label="Vilões", style=discord.ButtonStyle.secondary, custom_id="packs_villain")
    async def villain_packs(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self.bot.get_cog("PackView")
        if cog:
            await cog.show_packs_embed(interaction, "villain", 0, update=True)

    @discord.ui.button(label="Misto", style=discord.ButtonStyle.secondary, custom_id="packs_mixed")
    async def mixed_packs(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self.bot.get_cog("PackView")
        if cog:
            await cog.show_packs_embed(interaction, "mixed", 0, update=True)

class PackBuyButton(Button):
    def __init__(self, bot, pack_type, current_page):
        super().__init__(label="Comprar", style=discord.ButtonStyle.success)
        self.bot = bot
        self.pack_type = pack_type
        self.current_page = current_page

    def get_star_limit(self, rarity: str) -> int:
        return {
            "common": 50,
            "uncommon": 30,
            "rare": 10,
            "epic": 5,
            "legendary": 2
        }.get(rarity, 1)

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        db = get_db()

        with open("data/packs.json", "r", encoding="utf-8") as f:
            all_packs = json.load(f)

        type_map = {
            "hero": "Hero Packs",
            "villain": "Villain Packs",
            "mixed": "Themed Packs"
        }

        pack_list = all_packs.get(type_map.get(self.pack_type), [])
        if not pack_list or self.current_page >= len(pack_list):
            return await interaction.response.send_message("❌ Pacote inválido.", ephemeral=True)

        pack = pack_list[self.current_page]
        price = pack["price"]

        user = await db["users"].find_one({"_id": user_id})
        if not user:
            return await interaction.response.send_message("Você não está registrado!", ephemeral=True)

        if user.get("coins", 0) < price:
            return await interaction.response.send_message("💸 Você não tem moedas suficientes.", ephemeral=True)

        rarities = list(pack["probabilities"].keys())
        weights = list(pack["probabilities"].values())
        chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]
        db_rarity = RARITY_MAP[chosen_rarity]

        if self.pack_type == "hero":
            query = {"type": "hero", "rarity": db_rarity}
        elif self.pack_type == "villain":
            query = {"type": "villain", "rarity": db_rarity}
        else:
            query = {"rarity": db_rarity}

        personagens = await db["characters"].find(query).to_list(length=100)
        if not personagens:
            return await interaction.response.send_message("❌ Nenhum personagem encontrado.", ephemeral=True)

        personagem = random.choice(personagens)

        existing_char = None
        for p in user["collection"]:
            if p["_id"] == personagem["_id"]:
                existing_char = p
                break

        if existing_char:
            if "stars" not in existing_char:
                existing_char["stars"] = 0

            current_stars = existing_char["stars"]
            max_stars = self.get_star_limit(existing_char["rarity"])

            if current_stars < max_stars:
                existing_char["stars"] += 1

                await db["users"].update_one(
                    {"_id": user_id},
                    {
                        "$set": {"collection": user["collection"]},
                        "$inc": {
                            "coins": -price,
                            "power": personagem.get("power_base", 0)
                        }
                    }
                )

                embed = discord.Embed(
                    title="⭐ Evolução de Personagem!",
                    description=(
                        f"Você já tinha **{personagem['name']}**!\n"
                        f"Aumentou para **{existing_char['stars']}** estrelas."
                    ),
                    color=discord.Color.orange()
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Personagem no Máximo!",
                    description=(
                        f"Você já possui **{personagem['name']}** com o número máximo de estrelas (**{max_stars}**).\n"
                        f"Nada foi alterado."
                    ),
                    color=discord.Color.red()
                )
        else:
            personagem["stars"] = 0
            await db["users"].update_one(
                {"_id": user_id},
                {
                    "$push": {"collection": personagem},
                    "$inc": {
                        "coins": -price,
                        "power": personagem.get("power_base", 0)
                    }
                }
            )

            embed = discord.Embed(
                title="🎉 Personagem Obtido!",
                description=(
                    f"Você abriu o **{pack['name']}** e recebeu:\n"
                    f"**{personagem['name']}**\n"
                    f"Raridade: `{personagem['rarity'].capitalize()}`\n"
                    f"Poder: `{personagem['power_base']}`"
                ),
                color=discord.Color.green()
            )

        updated_user = await db["users"].find_one({"_id": user_id})
        new_power = calculate_total_power(updated_user.get("collection", []))

        # Atualizar o poder no banco
        await db["users"].update_one(
            {"_id": user_id},
            {"$set": {"power": new_power}}
        )

        await check_rank_promotion(self.bot, int(user_id), user.get("power", 0), new_power, interaction.channel)

        if personagem.get("image"):
            embed.set_image(url=personagem["image"])

        await interaction.response.send_message(embed=embed)


class PackPaginationView(View):
    def __init__(self, bot, pack_type, current_page, total_pages):
        super().__init__(timeout=None)
        self.bot = bot
        self.pack_type = pack_type
        self.current_page = current_page
        self.total_pages = total_pages

        
        self.add_item(PackBuyButton(bot, pack_type, current_page))

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary, custom_id="previous")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            cog = self.bot.get_cog("PackView")
            if cog:
                await cog.show_packs_embed(interaction, self.pack_type, self.current_page, update=True)

    @discord.ui.button(label="🏠 Menu", style=discord.ButtonStyle.secondary, custom_id="menu")
    async def menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self.bot.get_cog("PackMenu")
        if cog:
            embed = discord.Embed(
                title="📦 Loja de Pacotes",
                description=(
                    "Escolha uma categoria de pacotes para visualizar os personagens disponíveis:\n\n"
                    "**Heróis**  -  Os guardiões da justiça!\n"
                    "**Vilões**  -  Os mestres do caos!\n"
                    "**Misto**   -  Um pouco de tudo!"
                ),
                color=discord.Color.gold()
            )
            embed.set_footer(text="Use os botões abaixo para navegar.")
            await interaction.response.edit_message(embed=embed, view=PackMenuView(self.bot))


    @discord.ui.button(label="Próximo ➡️", style=discord.ButtonStyle.secondary, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            cog = self.bot.get_cog("PackView")
            if cog:
                await cog.show_packs_embed(interaction, self.pack_type, self.current_page, update=True)


class PackMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_pack_menu(self, destination):
        embed = discord.Embed(
            title="📦 Loja de Pacotes",
            description=(
                "Escolha uma categoria de pacotes para visualizar os personagens disponíveis:\n\n"
                "**Heróis**  -  Os guardiões da justiça!\n"
                "**Vilões**  -  Os mestres do caos!\n"
                "**Misto**   -  Um pouco de tudo!"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Use os botões abaixo para navegar.")
        await destination.send(embed=embed, view=PackMenuView(self.bot))


    @commands.command(name="packs")
    async def packs(self, ctx):
        await self.send_pack_menu(ctx)


class PackView(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def show_packs_embed(self, interaction: discord.Interaction, pack_type: str, page: int, update: bool = False):
        with open("data/packs.json", "r", encoding="utf-8") as f:
            all_packs = json.load(f)

        type_map = {
            "hero": "Hero Packs",
            "villain": "Villain Packs",
            "mixed": "Themed Packs"
        }

        pack_key = type_map.get(pack_type)
        pack_list = all_packs.get(pack_key, [])

        if not pack_list or page < 0 or page >= len(pack_list):
            await interaction.response.send_message("Pacote não encontrado.", ephemeral=True)
            return

        pack = pack_list[page]
        raridades = ", ".join(f"`{r}`" for r in pack["rarities"])
        probs = "\n".join([f"**{k}**: {v}%" for k, v in pack["probabilities"].items()])

        embed = discord.Embed(
            title=f"📦 {pack['name']} - 💰 {pack['price']} moedas",
            description=f"**Raridades:** {raridades}\n{probs}",
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Página {page + 1} de {len(pack_list)}")

        view = PackPaginationView(self.bot, pack_type, page, len(pack_list))

        await interaction.response.edit_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(PackMenu(bot))
    await bot.add_cog(PackView(bot))
