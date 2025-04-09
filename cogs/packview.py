import discord
from discord.ext import commands
from discord.ui import View, Button
import json

# View do menu principal
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

# View da paginação de pacotes
class PackPaginationView(View):
    def __init__(self, bot, pack_type, current_page, total_pages):
        super().__init__(timeout=None)
        self.bot = bot
        self.pack_type = pack_type
        self.current_page = current_page
        self.total_pages = total_pages

        # Botão de compra (sem ação ainda)
        self.add_item(Button(label="Comprar", style=discord.ButtonStyle.success, disabled=True))

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
