import asyncio
import os
import re
import discord
import random
import yt_dlp as youtube_dl
from discord import FFmpegOpusAudio
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

    
async def play_song(ctx, url, duration=15, max_filesize_mb=3):
    voice_channel = ctx.author.voice.channel

    ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    }
    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    YDL_OPTIONS = {'format': f'bestaudio[filesize<{max_filesize_mb}M]/best', 'noplaylist': 'True'}
    # audio, info = get_player(url)
    # with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
    #     info = ydl.extract_info(url, download=False)
    info = ytdl.extract_info(url, download=False)
    video_duration = info['duration']
    start_time = random.randint(0, max(0, video_duration - duration))

    FFMPEG_OPTS = {
        'before_options': (
            '-reconnect 1 '
            '-reconnect_streamed 1 '
            '-reconnect_delay_max 5 '
            # '-copyts '  # Preserve timestamps
            # f'-ss {start_time}'  # Moved seek to before_options
        ),
        'options': (
            '-vn '  # No video
            f'-t {duration} '  # Duration
            # '-ar 32000 '  # Lowered sample rate from 48000
            # '-ac 1 '      # Mono instead of stereo
            # '-b:a 64k '   # Lowered bitrate from 128k
            # '-bufsize 32k '  # Reduced buffer size
            # '-af "volume=0.5,loudnorm=I=-30:TP=-9:LRA=11"'  # Adjusted normalization
        )
    }

    audio = discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTS)

    try:
        voice_client = await voice_channel.connect()
        # Wait a short moment for the connection to stabilize
        # await asyncio.sleep(0.5)
    except discord.ClientException:
        voice_client = ctx.guild.voice_client

    # if voice_client.is_playing():
    #     voice_client.stop()

    
    # def after_playing(error):
    #     if error:
    #         print(f"Error in playback: {error}")
    #     # Create cleanup coroutine
    #     coro = voice_client.disconnect()
    #     # Schedule the coroutine to run
    #     fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    #     try:
    #         fut.result()
    #     except:
    #         pass

    def after_playing(error):
        if error:
            print(f"Error in playback: {error}")
        voice_client.stop()

    # Store audio reference in voice_client to prevent garbage collection
    play_song._clients[voice_client.guild.id] = voice_client
    import time
    print(time.time())
    voice_client.play(discord.PCMVolumeTransformer(audio, volume=0.1), after=after_playing)
    print(time.time())

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
    async def disconnect(ctx):
        voice_client = ctx.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()

    @bot.command()
    async def pool(ctx):
        songs_ids = state_manager.search_songs(**song_requirements)
        all_song_ids = state_manager.search_songs(song_type=song_requirements["song_type"])
        embed = discord.Embed(
            title="Available Anime Pool!",
            description=f"Pool Size: {len(songs_ids)} out of {len(all_song_ids)} songs",
            color=discord.Color.blue()
        )

        embed.add_field(    
            name="Members:",
            value=f"{song_requirements['members']}",
            inline=False
        )

        embed.add_field(    
            name="Popularity:",
            value=f"{song_requirements['popularity']}",
            inline=False
        )

        embed.add_field(    
            name="Year:",
            value=f"{song_requirements['year']}",
            inline=False
        )

        embed.add_field(    
            name="Rank:",
            value=f"{song_requirements['rank']}",
            inline=False
        )   

        embed.add_field(    
            name="Score:",
            value=f"{song_requirements['score']}",
            inline=False
        )

        embed.add_field(    
            name="Song Type:",
            value=f"{song_requirements['song_type']}",
            inline=False
        )

        await ctx.send(embed=embed)


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

        try:
            song_name, singer = song_query.split("by")
        except:
            song_name = ""
            singer = ""
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
            value=f"||{title} (https://myanimelist.net/anime/{mal_id})||", 
            inline=False
        )

        await ctx.send(embed=embed)

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(video_url)
        await play_song(ctx, video_url, **aniguesser_options)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

    bot_token = os.environ.get('ANIGUESSER_TOKEN')
    if bot_token is None:
        raise ValueError("Environment variable ANIGUESSER_TOKEN not set!")

    state_manager = StateManager(state_path)
    play_song._clients = {}

    bot.run(bot_token)

def main():
    dispatch_command(run_bot)


if __name__ == "__main__":
    # Run the bot
    main()
