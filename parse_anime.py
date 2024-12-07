import time
import json
from mal import Anime
from argh import arg, dispatch_command

def find_mal_entries(low_limit=12500, high_limit=15000):
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
            print(f"Found cache with {len(anicache["anime"])} entries.")

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

def cache(
    state_path: "Path to cache anime information"="anicache.json",
    wait_time: "Time to wait between requests"=4.0
):
    anicache = load_cache(state_path)
    highest_mal_id = find_mal_entries()
    parse_ids = list(range(1, highest_mal_id + 1))
    ignore_ids = [int(mal_id) for mal_id in anicache["anime"] if anicache["anime"][mal_id]["status"] in ["Finished Airing"]]
    parse_ids = list(set(parse_ids) - set(ignore_ids))
    nonexistent_ids = [int(mal_id) for mal_id in anicache["nonexistent"]]
    parse_ids = list(set(parse_ids) - set(nonexistent_ids))

    for mal_id in parse_ids:
        time.sleep(wait_time)

        try:
            anime = Anime(mal_id)
        except ValueError as e:
            print(f"ID {mal_id} not found, ignoring")
            anicache["nonexistent"].append(mal_id)
            continue
        except Exception as e:
            print(f"Error with ID {mal_id}: {e}")
            anicache["errors"].append(mal_id)
            continue

        entry = create_anime_entry(anime)

        print(mal_id, entry["title"])
        anicache["anime"][mal_id] = entry
        if mal_id in anicache["errors"]:
            anicache["errors"].remove(mal_id)

        if len(anicache["anime"]) % 100 == 0:
            print("Saving checkpoint")
            save_cache(anicache, state_path)

    save_cache(anicache, state_path)

def main():
    dispatch_command(cache)

if __name__ == "__main__":
    # Run the bot
    main()


