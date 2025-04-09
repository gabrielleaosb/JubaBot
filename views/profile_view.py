import discord
from discord.ui import View, Button
from discord import Interaction
from database.db import get_db
from utils.star_emoji import get_star_display


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

    async def send_page(self, interaction: Interaction):
        if self.page < 0 or self.page >= len(self.collection):
            return await interaction.response.send_message("❌ Página inválida.", ephemeral=True)

        char = self.collection[self.page]

        name = char.get("name", "Desconhecido")

        power_base = char.get("power_base", 0)
        stars = char.get("stars", 0)
        power = int(power_base * (1 + stars * 0.1))
        stars_display = get_star_display(stars)

        image = char.get("image", "")
        tipo = "Herói" if char.get("type") == "hero" else "Vilão"

        embed = discord.Embed(
            title=f"🎴 Coleção de {interaction.user.display_name}",
            description=(
                f"**{name}** {stars_display}\n"
                f"Tipo: **{tipo}**\n\n"
                f"Poder: `{power}`"
            ),
            color=discord.Color.purple()
        )

        if image:
            embed.set_image(url=image)

        embed.set_footer(text=f"Página {self.page + 1} de {len(self.collection)}")

        await interaction.response.edit_message(embed=embed, view=self)



class PreviousButton(Button):
    def __init__(self, view: CollectionPaginationView):
        super().__init__(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
        self.view_ref = view

    async def callback(self, interaction: Interaction):
        if str(interaction.user.id) != self.view_ref.user_id:
            return await interaction.response.send_message("❌ Isso não é para você!", ephemeral=True)

        if self.view_ref.page > 0:
            self.view_ref.page -= 1
            self.view_ref.update_buttons()
            await self.view_ref.send_page(interaction)


class NextButton(Button):
    def __init__(self, view: CollectionPaginationView):
        super().__init__(label="Próximo ➡️", style=discord.ButtonStyle.secondary)
        self.view_ref = view

    async def callback(self, interaction: Interaction):
        if str(interaction.user.id) != self.view_ref.user_id:
            return await interaction.response.send_message("❌ Isso não é para você!", ephemeral=True)

        if self.view_ref.page < self.view_ref.total_pages - 1:
            self.view_ref.page += 1
            self.view_ref.update_buttons()
            await self.view_ref.send_page(interaction)


class ProfileView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎴 Ver Coleção", style=discord.ButtonStyle.primary)
    async def view_collection(self, interaction: Interaction, button: Button):
        db = get_db()
        user_id = str(interaction.user.id)
        user = await db["users"].find_one({"_id": user_id})

        if not user or not user.get("collection"):
            return await interaction.response.send_message("❌ Você não possui personagens em sua coleção!", ephemeral=True)

        collection = user["collection"]
        view = CollectionPaginationView(user_id, collection, 0)

        await view.send_page(interaction)
