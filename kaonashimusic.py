import discord
import youtube_dl
import asyncio

from discord import FFmpegPCMAudio
from discord.ext import commands
from urllib.error import HTTPError

# YouTube_dl options
ytdlFormat = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
# FFmpeg options
FFmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
# Structure to keep track of queued songs
songQueue = {}

class ErrorHandler(commands.Cog, name='Erro'):
    def __init__(self, client):
        self.bot = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # If user uses an unknown command
        if isinstance(error, commands.CommandNotFound):
            message = "Não é um comando."
        else:
            message = "Algo deu errado."

        await ctx.send(message)

class Commands(commands.Cog, name='comandos'):
    def __init__(self, client):
        self.bot = client
        self.voice = None
        self.channel = None
        self.client = discord.Client()

    def next_song(self, ctx):
        if len(songQueue) > 0:
            title = next(iter(songQueue))
            song = songQueue.pop(next(iter(songQueue)))
            try:
                self.voice.play(song, after=lambda x=None: self.next_song(ctx))
                self.client.loop.create_task(
                    self.channel.send("Tocando agora: " + title))
            except discord.errors.ClientException:
                return

    @staticmethod
    def search(url):
        with youtube_dl.YoutubeDL(ytdlFormat) as dl:
            try:
                info = dl.extract_info(url, download=False)
                title = info.get('title', None)
                iUrl = info['formats'][0]['url']
    
                source = FFmpegPCMAudio(iUrl, **FFmpeg_opts)
                songQueue[title] = source

            except HTTPError.code == 403:
                return

            except KeyError:
                return
        return title

    @commands.Cog.listener()
    async def on_message(self, ctx):

        if ctx.content.startswith('!') and ctx.content.strip() != "!play" and not ctx.content.startswith("!play "):
            try:
                await asyncio.sleep(10)
                await ctx.delete()
            except discord.errors.NotFound:
                pass

        elif ctx.author.bot:
            try:
                await asyncio.sleep(10)
                await ctx.delete()
            except discord.errors.NotFound:
                pass

    @commands.command()
    async def play(self, ctx, url: str):

        title = self.search(url)

        try:
            self.voice = await ctx.message.author.voice.channel.connect()
        except discord.ClientException:
            self.voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        channelID = ctx.channel.id
        self.channel = self.bot.get_channel(channelID)

        if ctx.voice_client.is_playing():
            message = "Musica: " + title + " foi adicionada a Fila. 🎶\nTamanho da Fila atual: " + str(len(songQueue))
            await ctx.send(message)

        else:
            if len(songQueue) > 0:
                    await asyncio.sleep(1)
                    self.voice.play(source=songQueue[title], after=lambda e: Commands.next_song(self, ctx))
                    self.voice.is_playing()
            else:
                message = "Fila está vazia."
                await ctx.send(message)

    @commands.command()
    async def skip(self, ctx):
        if not len(songQueue) > 0:
            await ctx.send("Fila está vazia, não há o que pular")
            return

        self.voice.stop()

        try:
            title = next(iter(songQueue))
            self.voice.play(songQueue[title])
            songQueue.pop(title)

            if len(songQueue) > 0:
                message = "Tamanho da fila atual: " + str(len(songQueue)) + "\nTocando agora" + title
            else:
                message = "Tocando agora: " + title

        except IndexError:
            return

        await ctx.send(message)

    @commands.command()
    async def queue(self, ctx):
        if not len(songQueue) > 0:
            await ctx.send("Não há Fila.")
            return
        else:
            await ctx.send("Fila atual: ")
            position = 1
            for i in songQueue:
                message = str(position) + ": " + i
                await ctx.send(message)

    @commands.command(name='cqueue')
    async def clear(self, ctx):
        songQueue.clear()
        await ctx.send("A Fila foi limpa.")

    @commands.command()
    async def pause(self, ctx):

        if self.voice.is_playing():
            self.voice.pause()
            message = "A música agora está pausada."
        else:
            message = "O bot não está tocando música no momento"

        await ctx.send(message)

    @commands.command()
    async def resume(self, ctx):

        if self.voice.is_paused():
            self.voice.resume()
        else:
            await ctx.send("O Kaonashi está tocando música no momento")
    
    @commands.command()
    async def stop(self, ctx):
        await self.clear(ctx)
        self.voice.stop()

    @commands.command()
    async def leave(self, ctx):
        # To disconnect the bot from the voice channel
        if self.voice:
            message = "Até mais!"
            await self.clear(ctx)
            await self.voice.disconnect()
        else:
            message = "No momento, não estou em um canal de voz"

        await ctx.send(message)

def setup(client):
     client.add_cog(Commands(client))