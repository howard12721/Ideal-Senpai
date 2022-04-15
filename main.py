#!/usr/bin/python
#coding:utf-8

import sqlite3

import discord
from discord.ext import commands

import traceback
import datetime
import pytz

INITIAL_EXTENSIONS = [
    'cogs.commands'
]

class MyBot(commands.Bot):

    def __init__(self, command_prefix):
        intents = discord.Intents.all()
        super().__init__(command_prefix, intents = intents)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()
        
        self.dbconnect = sqlite3.connect("data/members.db")

        cursor = self.dbconnect.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Members(id INTEGER PRIMARY KEY, period INTEGER, isAdmin BIT)')

    def isAdmin(self, user_id):
        cursor = self.dbconnect.cursor()
        cursor.execute('SELECT isAdmin FROM Members WHERE id = {}'.format(user_id))
        for row in cursor:
            return row[0]

    async def registMember(self, id: int, period: int, isAdmin: bool):
        cursor = self.dbconnect.cursor()
        cursor.execute('INSERT INTO Members values({}, {}, {})'.format(id, period, isAdmin))
        self.dbconnect.commit()
    
    async def on_ready(self):
        game = discord.Game("何か")
        await self.change_presence(status=discord.Status.idle, activity=game)
        print("BOTが正常に起動されました。")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.id == 964563519271993436:
            content = message.content
            period: int
            try:
                period = int(content)
            except ValueError:
                await message.channel.send(embed=discord.Embed(title="エラー: 無効な値です", description="あなたの所属している回を**半角数字**で入力してください\n例) 「127」", color=0xFF0000), delete_after=3)
                return
            if period <= 0 or period >= 300:
                await message.channel.send(embed=discord.Embed(title="エラー: 無効な値です", description="あなたの所属している回を**半角数字**で入力してください\n例) 「127」", color=0xFF0000), delete_after=3)
            cursor = self.dbconnect.cursor()
            cursor.execute('SELECT COUNT( * ) FROM Members WHERE id = {}'.format(message.author.id))
            for row in cursor:
                count = row[0]
            if count == 0:
                cursor.execute('INSERT INTO Members values ({}, {}, 0)'.format(message.author.id, period))
                self.dbconnect.commit()
                await message.channel.send(embed=discord.Embed(title="設定完了", description="あなたの所属を{}回に設定しました".format(period), color=0x59ff91), delete_after=3)
            else:
                cursor.execute('UPDATE Members SET period = {} WHERE id = {}'.format(period, message.author.id))
                self.dbconnect.commit()
                await message.channel.send(embed=discord.Embed(title="更新完了", description="あなたの所属を{}回に更新しました".format(period), color=0x59ff91), delete_after=3)
            
            targetMember: discord.Member = message.author
            now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
            year = now.year
            if now.month <= 9:
                year -= 1
            OBline = year-1896
            if period <= OBline:
                await targetMember.remove_roles(message.guild.get_role(903541322525315142))
                await targetMember.add_roles(message.guild.get_role(903542282370826281)) #OB role
            else:
                await targetMember.remove_roles(message.guild.get_role(903542282370826281))
                await targetMember.add_roles(message.guild.get_role(903541322525315142)) #現役 role

        await self.process_commands(message)

if __name__ == '__main__':
    bot = MyBot(command_prefix='c!')
    bot.run('TOKEN')
    bot.dbconnect.close()