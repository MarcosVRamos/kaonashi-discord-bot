# kaonashi-discord-bot

This is a Python script for a Discord bot that can play music in a voice channel, as well as perform other related functions. The script uses the Discord API, the youtube_dl library, and the asyncio library.

The bot is defined as a class that is a subclass of the Discord Cog class. The bot has several commands that it can respond to, such as "play," "pause," "resume," "stop," "skip," "queue," and "clear." The "play" command takes a YouTube URL and adds it to a queue, which the bot will play in sequence. The other commands control playback or manage the queue.


- Steps you need before starting the bot.

- install all libs.
- install ffmpeg on your operating system.
- Change the line where the token is by putting your discord application "bot.run('token')".
