import os
import time
import discord
import json
import random
from discord.ext import commands
from discord import FFmpegPCMAudio
from argh import arg, dispatch_command
from mal import Anime
from state_manager import StateManager
from youtube_search import YoutubeSearch

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

state_manager = None

def music_player(voice,author_channel):
    global music_queue
    while len(music_queue[author_channel]) != 0:
        current_url = music_queue[author_channel].pop(0)
        video, source = search(current_url)
        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                       'options': '-vn'}
        voice.play(FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: print('done', e))
        while voice.is_playing() == True:
            time.sleep(1)

def get_available(state, cache):
    available_ids = set(list(range(1, highest_mal_id + 1)))

    complete_ids = set(list(bot_state["complete"].keys()))
    available_ids = available_ids - complete_ids

    blacklist_ids = set(list(bot_state["blacklist"].keys()))
    available_ids = available_ids - blacklist_ids
    return list(all_ids - ignore_ids)


def run_bot(
    state_path: "Path to load and save state" = "anicache.json",
):
    global state_manager

    def aniguess():
        global state_manager
        songs_ids = state_manager.search_songs(rank=100)

        mal_id, song_index = random.sample(songs_ids, 1)[0]

        song = state_manager.query_song(mal_id, song_index)
        anime = state_manager.query_anime(mal_id)
        # await ctx.send(f"Song: {song}")
        print(anime["title"])
        print(anime["rank"])
        print(song)

        # available_ids = get_available(bot_state, anicache)

        top_result = YoutubeSearch(song, max_results=1).to_dict()
        video_id = top_result[0]["id"]

        print(f"https://www.youtube.com/watch?v={video_id}")

        # while True:
        #     chosen_id = random.sample(available_ids)

    async def play_song(ctx, url):
        # Check if user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return

        voice_channel = ctx.author.voice.channel

        # Connect to voice channel if not already connected
        try:
            voice_client = await voice_channel.connect()
        except discord.ClientException:
            voice_client = ctx.guild.voice_client

        # Stop any currently playing audio
        if voice_client.is_playing():
            voice_client.stop()

        # Create FFmpeg audio source from YouTube URL
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        YDL_OPTIONS = {'format': 'bestaudio'}

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            voice_client.play(source)

    # Event: Bot is ready and running
    # @bot.event
    # async def on_ready():
    #     print(f"Logged in as {bot.user}")
    #     load_cache()
    #     load_state()

    bot_token = os.environ.get('ANIGUESSER_TOKEN')
    if bot_token is None:
        raise ValueError("ANIGUESSER_TOKEN not set!")

    # bot.run(bot_token)

    state_manager = StateManager(state_path)
    aniguess()


def main():
    dispatch_command(run_bot)


if __name__ == "__main__":
    # Run the bot
    main()
