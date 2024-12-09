import asyncio
import os
import re
import discord
import random
import yt_dlp as youtube_dl
from discord import FFmpegPCMAudio
from discord.ext import commands
from argh import dispatch_command
from state_manager import StateManager
from youtube_search import YoutubeSearch

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

song_requirements = {
    "members": 100000,
    "popularity": None,
    "year": 1995,
    "rank": None,
    "score": 7.5,
    "song_type": "opening",
}

aniguesser_options = {
    "duration": 15
}

state_manager = None

def run_bot(
    state_path: "Path to load and save state" = "anicache.json",
):
    global state_manager

    @bot.command()
    async def get_song_requirements(ctx):
        global song_requirements
        await ctx.send(song_requirements)

    @bot.command()
    async def set_song_requirements(ctx, members: int, popularity: int, year: int, rank: int, score: float, song_type: str):
        global song_requirements
        song_requirements["members"] = members
        song_requirements["popularity"] = popularity
        song_requirements["year"] = year
        song_requirements["rank"] = rank
        song_requirements["score"] = score
        song_requirements["song_type"] = song_type
        await ctx.send(song_requirements)

    @bot.command()
    async def get_aniguesser_options(ctx):
        global aniguesser_options
        await ctx.send(aniguesser_options)

    @bot.command()
    async def set_aniguesser_options(ctx, duration: int):
        global aniguesser_options
        aniguesser_options["duration"] = duration
        await ctx.send(aniguesser_options)

    @bot.command()
    async def merge_state(ctx, state_path_1: "Path to merge anime information"="anicache.json", state_path_2: "Path to merge anime information"="anicache_merged.json"):
        global state_manager
        state_manager.merge_state(state_path_1, state_path_2)
        await ctx.send("State merged")

    @bot.command()
    async def aniguess(ctx):
        global state_manager
        global aniguesser_options
        songs_ids = state_manager.search_songs(**song_requirements)

        mal_id, song_index = random.sample(songs_ids, 1)[0]

        song_query = state_manager.query_song(mal_id, song_index)
        anime = state_manager.query_anime(mal_id)
        # await ctx.send(f"Song: {song}")
        print(anime["title"])
        print(anime["rank"])

        print(song_query)
        song_query = song_query.replace("\"", "")
        song_query = re.sub(r"(\(eps \d+.*?\))", "", song_query)
        print(song_query)
        top_result = YoutubeSearch(song_query, max_results=1).to_dict()
        print(top_result)
        video_id = top_result[0]["id"]

        embed = discord.Embed(
            title="Guess the Anime!",
            description="Listen to the clip and guess the anime",
            color=discord.Color.blue()
        )
        
        premiered = anime['premiered']
        embed.add_field(
            name="Hint 1: Premier Date", 
            value=f"||{premiered}||", 
            inline=False
        )

        song_name, singer = song_query.split("by")
        embed.add_field(    
            name="Hint 2: Song Name",
            value=f"||{song_name.strip()}||",
            inline=False
        )

        embed.add_field(    
            name="Hint 3: Singer",
            value=f"||{singer.strip()}||",
            inline=False
        )

        title = anime['title']
        embed.add_field(
            name="Answer!", 
            value=f"||{title}||", 
            inline=False
        )

        await ctx.send(embed=embed)

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(video_url)
        await play_song(ctx, video_url, **aniguesser_options)

    async def play_song(ctx, url, duration=15):
        voice_channel = ctx.author.voice.channel

        try:
            voice_client = await voice_channel.connect()
        except discord.ClientException:
            voice_client = ctx.guild.voice_client

        if voice_client.is_playing():
            voice_client.stop()

        YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            video_duration = info['duration']
            start_time = random.randint(0, max(0, video_duration - duration))
            
            FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                       'options':  f'-vn -ss {start_time} -t {duration}'}

            # TODO: Why is the sound going in and out?
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            voice_client.play(FFmpegPCMAudio(info['url'], **FFMPEG_OPTS))

            # Optional: Stop after duration
            await asyncio.sleep(duration)
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

    bot_token = os.environ.get('ANIGUESSER_TOKEN')
    if bot_token is None:
        raise ValueError("Environment variable ANIGUESSER_TOKEN not set!")

    state_manager = StateManager(state_path)

    bot.run(bot_token)

def main():
    dispatch_command(run_bot)


if __name__ == "__main__":
    # Run the bot
    main()
