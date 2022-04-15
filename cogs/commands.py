import discord
from discord.ext import commands
from discord.ext import tasks

import sys
import traceback

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("pong!")

    @commands.command()
    async def update(self, ctx):
        if not self.bot.isAdmin(ctx.author.id):
            return

        await ctx.send(embed=discord.Embed(title="BOTを再起動します。(未実装で～～～～す)", description="これには1分程かかる場合があります。"))

    @commands.command()
    async def register(self, ctx, id: int, period: int):
        if not self.bot.isAdmin(ctx.author.id):
            return

        await self.bot.registMember(id, period, True)

    @commands.command()
    async def sql(self, ctx, *, script: str):
        if not self.bot.isAdmin(ctx.author.id):
            return

        cursor = self.bot.dbconnect.cursor()
        try:
            cursor.execute(script)
            self.bot.dbconnect.commit()
            output = ""
            for row in cursor:
                for value in row:
                    output += "(**{}**) ".format(value)
                output += "\n"
            await ctx.send(embed=discord.Embed(title="出力", description=output, color=0x111166))
        except Exception:
            traceback.print_exc()
            await ctx.send(embed=discord.Embed(title="例外をキャッチ！", description="`{}`".format(sys.exc_info()), color=0xFF0000))

def setup(bot):
    bot.add_cog(Commands(bot))