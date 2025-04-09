import discord
from discord.ext import commands


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📖 Central de Comandos",
            description="Veja abaixo os comandos disponíveis e o que cada um faz:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Pacotes",
            value=(
                "`!packs`  —  Abre a loja de pacotes para escolher entre heróis, vilões ou misto.\n"
            ),
            inline=False
        )

        embed.add_field(
            name="Economia",
            value=(
                "`!rewards`  —  Exibe todas as formas disponíveis de ganhar moedas e seus respectivos tempos de recarga (cooldown).\n"
                "`!daily`  —  Resgata uma quantia de moedas diariamente. Pode ser usado uma vez por dia.\n"
                "`!work`  —  Realiza um trabalho aleatório; quanto mais raro o trabalho, maior a recompensa em moedas."
            ),
            inline=False
        )

        embed.add_field(
            name="Rank",
            value=(
                "`!rank`  `!r`—  Mostra o ranking dos jogadores com mais poder.\n"
                "`!infopower`  `!ip` —  Mostra as classificações de poder e os requisitos para cada uma."
            ),
        )

        embed.add_field(
            name="Outros",
            value=(
                "`!profile`  `!p` —  Veja seu perfil com suas estatísticas.\n"
                "`!help`  —  Mostra esta mensagem de ajuda."
            ),
            inline=False
        )

        embed.set_footer(text="Use os comandos com responsabilidade e divirta-se!")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
