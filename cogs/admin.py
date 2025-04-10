import discord
from discord.ext import commands
from database.db import get_db
from utils.power import check_rank_promotion, calculate_total_power 

OWNER_ID = 1151268641401221241

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        """Reseta o histórico de rolls de um usuário (ou o seu próprio)"""
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

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
