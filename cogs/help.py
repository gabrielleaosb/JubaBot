import discord
from discord.ext import commands


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="**Central de Comandos**",
            description="Aqui estão todos os comandos disponíveis. Se precisar de mais ajuda, não hesite em perguntar!",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🎲 **Roll**",
            value=(
                "`!roll`  `!r`  —  Realiza um roll para obter um personagem aleatório com base em sua raridade.\n"
                "Você tem **10 rolls gratuitos por hora**! Após isso, será necessário esperar ou usar moedas para mais rolls."
            ),
            inline=False
        )

        embed.add_field(
            name="💰 **Economia**",
            value=(
                "`!rewards`  —  Exibe todas as formas de ganhar moedas e seus respectivos tempos de recarga (cooldown).\n"
                "`!daily`  —  Resgata uma quantia de moedas diariamente. Pode ser usado uma vez por dia.\n"
                "`!work`  —  Realiza um trabalho aleatório; quanto mais raro o trabalho, maior a recompensa em moedas."
            ),
            inline=False
        )

        embed.add_field(
            name="🏆 **Rank**",
            value=(
                "`!rank`  `!r`  —  Mostra o ranking dos jogadores com mais poder.\n"
                "`!infopower`  `!ip`  —  Mostra as classificações de poder e os requisitos para cada uma."
            ),
            inline=False
        )

        embed.add_field(
            name="🦸‍♂️🦹‍♂️ **Personagens**",
            value=(
                "`!chars`  —  Lista todos os personagens da coleção (heróis e vilões).\n"
                "`!heroes`  —  Lista apenas os heróis da coleção.\n"
                "`!villains`  —  Lista apenas os vilões da coleção."
            ),
            inline=False
        )

        embed.add_field(
            name="👤 **Outros**",
            value=(
                "`!profile`  `!p`  —  Veja seu perfil com suas estatísticas.\n"
                "`!help`  —  Mostra esta mensagem de ajuda."
            ),
            inline=False
        )

        embed.set_footer(text="Use os comandos com responsabilidade e divirta-se! 🚀")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
