import argh
import re
import time
import json
import requests
from mal import Anime
from argh import arg, dispatch_commands
from state_manager import StateManager

def find_mal_entries(low_limit=12500, high_limit=15000):
    """Find the highest mal id that exists.

    DO NOT USE.

    TODO: This does not account for deleted entries. Instead find newest entry directly.
    """
    highest_found = low_limit
    curr_low = low_limit
    curr_high = high_limit
    while curr_low < curr_high:
        mid = (curr_low + curr_high) // 2
        try:
            anime = Anime(mid)
            highest_found = max(highest_found, mid)
        except ValueError as e:
            # The id is too high
            print(f'ID {mid} not found, going down')
            curr_high = mid - 1
            continue
        except Exception as e:
            print(e)
            return curr_low
        print(f'ID {mid} found, going up')
        curr_low = mid + 1
    return highest_found

def find_newest_mal_entry(url="https://myanimelist.net/anime.php?o=9&c%5B0%5D=a&c%5B1%5D=d&cv=2&w=1"):
    """Find the newest mal id that exists.
    """
    response = requests.get(url)

    matches = re.findall(r"https://myanimelist.net/anime/(\d+)", response.text)
    if matches:
        highest_id = max([int(i) for i in matches])
    else:
        highest_id = -1

    return highest_id

def create_anime_entry(anime):
    return {
        "aired": anime.aired,
        "endings": [i for i in anime.ending_themes],
        "openings": [i for i in anime.opening_themes],
        "mal_id": anime.mal_id,
        "members": anime.members,
        "popularity": anime.popularity,
        "premiered": anime.premiered,
        "rank": anime.rank,
        "score": anime.score,
        "status": anime.status,
        "themes": anime.themes,
        "title": anime.title,
        "title_english": anime.title_english,
        "title_japanese": anime.title_japanese,
    }

def load_cache(
    state_path
):
    try:
        with open(state_path, "r") as file:
            anicache = json.load(file)
            anicache_size = len(anicache["anime"])
            print(f"Found cache with {anicache_size} entries.")

    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Found no previously existing cache, creating new.")
        anicache = {"anime": {}, "errors": [], "nonexistent": []}

    return anicache


def save_cache(
    anicache,
    state_path
):
    try:
        with open(state_path, 'w') as file:
            json.dump(anicache, file, indent=4)
            print("Cache saved successfully.")
    except Exception as e:
        print(f"Error saving state: {e}")

def get_anime(mal_id, retries=3, retry_wait=3.0):
    try:
        anime = Anime(mal_id)
        return anime
    except TypeError as e:
        print(f"Rate limited: {e}")
        if retries > 0:
            time.sleep(retry_wait)
            return get_anime(mal_id, retries - 1, retry_wait)
        else:
            raise Exception(f"Could not get anime after being rate limited")

def cache(
    state_path: "Path to cache anime information"="anicache.json",
    wait_time: "Time to wait between each ID"=4.0,
    retry_wait: "Time to wait after being rate limited"=60.0,
    checkpoint_interval: "Number of entries to save after"=100,
    starting_mal_id: "Starting mal id to parse"=1,
    ending_mal_id: "Highest mal id to parse"=-1,
    redo_finished: "Reparse finished anime"=False,
    redo_airing: "Reparse airing anime"=False,
    redo_upcoming: "Reparse upcoming anime"=False,
    descending_order: "Order to iterate over IDs"=True,
):
    ignore_status = []
    if not redo_finished:
        ignore_status.append("Finished Airing")
    if not redo_airing:
        ignore_status.append("Currently Airing")
    if not redo_upcoming:
        ignore_status.append("Not yet aired")
    if ending_mal_id == -1:
        ending_mal_id = find_newest_mal_entry()

    anicache = load_cache(state_path)

    print(f"Parsing from {starting_mal_id} to {ending_mal_id}")
    parse_ids = list(range(starting_mal_id, ending_mal_id + 1))
    ignore_ids = [int(mal_id) for mal_id in anicache["anime"] if anicache["anime"][mal_id]["status"] in ignore_status]
    parse_ids = list(set(parse_ids) - set(ignore_ids))
    nonexistent_ids = [int(mal_id) for mal_id in anicache["nonexistent"]]
    parse_ids = list(set(parse_ids) - set(nonexistent_ids))
    parse_ids.sort(reverse=descending_order)

    for mal_id in parse_ids:
        time.sleep(wait_time)
        try:
            anime = get_anime(mal_id, retries=3, retry_wait=retry_wait)
            if anime is None:
                continue
        except ValueError as e:
            print(f"ID {mal_id} not found, ignoring")
            anicache["nonexistent"].append(mal_id)
            continue
        except Exception as e:
            print(f"Error with ID {mal_id}: {e}")
            anicache["errors"].append(mal_id)
            continue

        entry = create_anime_entry(anime)

        print(mal_id, entry["title"], entry["status"])
        anicache["anime"][mal_id] = entry
        if mal_id in anicache["errors"]:
            anicache["errors"].remove(mal_id)

        if len(anicache["anime"]) % checkpoint_interval == 0:
            print("Saving checkpoint")
            save_cache(anicache, state_path)

    save_cache(anicache, state_path)

def merge(
    state_path_1: "Path to cache anime information"="anicache.json",
    state_path_2: "Path to merge anime information"="anicache_merged.json",
    save_path: "Path to save merged anime information"=None,
):
    anicache = StateManager.merge_state(state_path_1, state_path_2)
    StateManager.save_state(anicache, state_path_1 if save_path is None else save_path)

def main():
    parser = argh.ArghParser()
    parser.add_commands([cache, merge])
    parser.set_default_command(cache)
    parser.dispatch()

if __name__ == "__main__":
    # Run the bot
    main()


