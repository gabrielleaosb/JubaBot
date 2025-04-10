import discord
from discord.ui import View, Button
from discord import Interaction
from database.db import get_db
from utils.star_emoji import get_star_display
from bson import ObjectId

class CollectionPaginationView(View):
    def __init__(self, user_id: str, collection: list, page: int = 0):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.collection = collection
        self.page = page
        self.total_pages = len(collection)
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        self.add_item(PreviousButton(self))
        self.add_item(NextButton(self))
    
    def _format_stars_display(self, stars: int) -> str:
        """Formata a exibição de estrelas com quebra de linha a cada 10 estrelas"""
        star_emoji = "⭐"
        max_stars_per_line = 10
        
        full_lines = stars // max_stars_per_line
        remaining_stars = stars % max_stars_per_line
        
        lines = []
        for _ in range(full_lines):
            lines.append(star_emoji * max_stars_per_line)
        
        if remaining_stars > 0:
            lines.append(star_emoji * remaining_stars)
        
        return "\n".join(lines)

    async def send_page(self, interaction: Interaction):
        if not self.collection:
            return await interaction.response.send_message("❌ Coleção vazia.", ephemeral=True)

        # Garante que a página está dentro dos limites (com comportamento circular)
        self.page = self.page % len(self.collection)
        if self.page < 0:
            self.page = len(self.collection) - 1

        char = self.collection[self.page]
        
        # Verifica se é um ObjectId e busca o personagem completo se necessário
        if isinstance(char, ObjectId):
            db = get_db()
            char = await db["characters"].find_one({"_id": char})
            if not char:
                return await interaction.response.send_message("❌ Personagem não encontrado.", ephemeral=True)

        name = char.get("name", "Desconhecido")
        rarity = char.get("rarity", "common").lower()  # Padroniza para lowercase
        power_base = char.get("power_base", 0)
        stars = char.get("stars", 0)  # Garante que stars existe, padrão 0
        power = int(power_base * (1 + stars * 0.1))
        image = char.get("image", "")
        type = char.get("type", "Desconhecido")
        
        rarity_colors = {
            "common": discord.Color.light_grey(),
            "uncommon": discord.Color.green(),
            "rare": discord.Color.blue(),
            "epic": discord.Color.purple(),
            "legendary": discord.Color.gold()
        }   

        embed_color = rarity_colors.get(rarity, discord.Color.default())

        embed = discord.Embed(
            title=f"🎴 Coleção de {interaction.user.display_name}",
            description=(
                f"**{name}**\n"
                f"{self._format_stars_display(stars)}\n"
                f"Tipo: **{type.capitalize()}**\n"
                f"Raridade: **{rarity.capitalize()}**\n\n"
                f"Poder: `{power}`\n"
                f"Estrelas: `{stars}`"
            ),
            color=embed_color
        )

        if image:
            embed.set_image(url=image)

        embed.set_footer(text=f"{self.page + 1}/{len(self.collection)}")

        await interaction.response.edit_message(embed=embed, view=self)


class PreviousButton(Button):
    def __init__(self, view: CollectionPaginationView):
        super().__init__(label="⬅️", style=discord.ButtonStyle.secondary)
        self.view_ref = view

    async def callback(self, interaction: Interaction):
        if str(interaction.user.id) != self.view_ref.user_id:
            return await interaction.response.send_message("❌ Isso não é para você!", ephemeral=True)

        self.view_ref.page -= 1
        self.view_ref.update_buttons()
        await self.view_ref.send_page(interaction)


class NextButton(Button):
    def __init__(self, view: CollectionPaginationView):
        super().__init__(label="➡️", style=discord.ButtonStyle.secondary)
        self.view_ref = view

    async def callback(self, interaction: Interaction):
        if str(interaction.user.id) != self.view_ref.user_id:
            return await interaction.response.send_message("❌ Isso não é para você!", ephemeral=True)

        self.view_ref.page += 1
        self.view_ref.update_buttons()
        await self.view_ref.send_page(interaction)


class ProfileView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Coleção", style=discord.ButtonStyle.primary)
    async def view_collection(self, interaction: Interaction, button: Button):
        db = get_db()
        user_id = str(interaction.user.id)
        user = await db["users"].find_one({"_id": user_id})

        if not user or not user.get("collection"):
            return await interaction.response.send_message("❌ Você não possui personagens em sua coleção!", ephemeral=True)

        # Garante que estamos trabalhando com a coleção completa
        collection = user["collection"]
        
        # Se a coleção contiver ObjectIds, precisamos buscar os personagens completos
        if collection and isinstance(collection[0], ObjectId):
            db = get_db()
            collection = await db["characters"].find({"_id": {"$in": collection}}).to_list(None)
            # Preserva as estrelas do usuário
            for char in collection:
                user_char = next((c for c in user["collection"] if isinstance(c, dict) and c.get("_id") == char["_id"]), None)
                if user_char:
                    char["stars"] = user_char.get("stars", 0)

        view = CollectionPaginationView(user_id, collection, 0)
        await view.send_page(interaction)