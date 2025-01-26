# AniGuess Discord Bot

A Discord bot that plays anime openings and endings within a discord channel in real time, challenging users to guess the anime.

## Features

- Plays random anime songs from MyAnimeList database
- Configurable requirements for song selection (popularity, score, etc.)
- Provides hints like premiere date and song name
- Uses YouTube for song playback

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt

# Additionally ffmpeg will be needed
```


2. Set up a Discord bot and get the token: https://discord.com/developers/applications

3. Add the token to your environment variables:

```bash
export ANIGUESSER_TOKEN=<your_token>
```

4. Parse the MyAnimeList database and cache data:

```bash
python parse_anime.py
```

*Note*: The above step may take a while (i.e. days) because of rate limiting via MAL. If you want to quickly start playing songs, [this is pre-parsed output which contains entries up until about mid-late 2024](https://drive.google.com/file/d/1hJ6RfZP5wrxuKmmyRdxXN8rjUyaLnSf2/view?usp=sharing)!

5. Run the bot:

```bash
python bot.py
```

## Discord Commands

Join a server and start guessing some anime, try it out with `!aniguess`. The bot will join the voice channel you are currently in and start playing a random song given the song requirements.

- `!aniguess` - Start a new guessing game
- `!get_song_requirements` - Show current song selection criteria
- `!set_song_requirements` - Update song selection criteria
- `!get_aniguesser_options` - Get the playback and guessing options
- `!set_aniguesser_options` - Update the playback and guessing options
- `!pool` - Get the size of the song pool
- `!disconnect` - Disconnect the bot from the voice channel

## Additional Notes and Improvements

- There are currently some performance issues with streaming audio to the voice channel that still need to be addressed
- Song and guessing options need to be expanded
