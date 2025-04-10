import discord
from discord.ext import commands
from discord.ui import View, Button
from database.db import get_db

class CharacterPaginator(discord.ui.View):
    def __init__(self, characters, timeout=60):
        super().__init__(timeout=timeout)
        self.characters = characters
        self.current_page = 0

    async def update_embed(self, interaction):
        character = self.characters[self.current_page]
        embed = discord.Embed(
            title=character["name"],
            description=(
                f"**Raridade:** {character['rarity'].capitalize()}\n"
                f"**Tipo:** {character['type'].capitalize()}\n"
                f"**Universo:** {character.get('universe', 'Desconhecido')}"
            ),
            color=discord.Color.blue()
        )
        if "image" in character and character["image"]:
            embed.set_image(url=character["image"].strip())  

        embed.set_footer(text=f"{self.current_page + 1}/{len(self.characters)}")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page < len(self.characters) - 1:
            self.current_page += 1
            await self.update_embed(interaction)


class CharacterView(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chars")
    async def list_characters(self, ctx):
        try:
            db = get_db()
            characters = await db["characters"].find().to_list(length=100)  

            if not characters:
                return await ctx.send("❌ Nenhum personagem encontrado.")

            view = CharacterPaginator(characters)
            first_embed = self._create_embed(characters[0])
            first_embed.set_footer(text=f"1/{len(characters)}")
            await ctx.send(embed=first_embed, view=view)
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao acessar o banco de dados: {str(e)}")

    @commands.command(name="heroes")
    async def list_heroes(self, ctx):
        try:
            db = get_db()
            # Filtra apenas os heróis
            heroes = await db["characters"].find({"type": "hero"}).to_list(length=100)

            if not heroes:
                return await ctx.send("❌ Nenhum herói encontrado.")

            view = CharacterPaginator(heroes)
            first_embed = self._create_embed(heroes[0])
            first_embed.set_footer(text=f"1/{len(heroes)}")
            await ctx.send(embed=first_embed, view=view)
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao acessar o banco de dados: {str(e)}")

    @commands.command(name="villains")
    async def list_villains(self, ctx):
        try:
            db = get_db()
            # Filtra apenas os vilões
            villains = await db["characters"].find({"type": "villain"}).to_list(length=100)

            if not villains:
                return await ctx.send("❌ Nenhum vilão encontrado.")

            view = CharacterPaginator(villains)
            first_embed = self._create_embed(villains[0])
            first_embed.set_footer(text=f"1/{len(villains)}")
            await ctx.send(embed=first_embed, view=view)
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao acessar o banco de dados: {str(e)}")

    def _create_embed(self, character):
        embed = discord.Embed(
            title=character["name"],
            description=(
                f"**Raridade:** {character['rarity'].capitalize()}\n"
                f"**Tipo:** {character['type'].capitalize()}\n"
                f"**Universo:** {character.get('universe', 'Desconhecido')}"
            ),
            color=discord.Color.blurple()
        )
        if "image" in character and character["image"]:
            embed.set_image(url=character["image"].strip())  
        return embed


async def setup(bot):
    await bot.add_cog(CharacterView(bot))
