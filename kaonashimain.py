import discord
import kaonashimusic

from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

cogs = [kaonashimusic]

@bot.event
async def on_ready():
    print(bot.user.name + ' ta On!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="🪙🪙🪙🪙🪙"))

@bot.command(name='c')
async def clear(ctx, amount=100):
    await ctx.channel.purge(limit=amount)
    await ctx.send(str(amount) + ' mensagens deletadas. 🧼🫧')

for i in range(len(cogs)):
    cogs[i].setup(bot)

bot.run('token')