# AniGuess Discord Bot

A Discord bot that plays anime openings and endings, challenging users to guess the anime.

## Features

- Plays random anime songs from MyAnimeList database
- Configurable requirements for song selection (popularity, score, etc.)
- Provides hints like premiere date and song name
- Uses YouTube for song playback

## Commands

- `!aniguess` - Start a new guessing game
- `!get_song_requirements` - Show current song selection criteria
- `!set_song_requirements` - Update song selection criteria

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up a Discord bot and get the token: https://discord.com/developers/applications

3. Add the token to your environment variables:

```bash
export ANIGUESSER_TOKEN=<your_token>
```

4. Parse the MyAnimeList database and cache data (this may take a while):

```bash
python parse_anime.py
```

5. Run the bot:

```bash
python bot.py
```
