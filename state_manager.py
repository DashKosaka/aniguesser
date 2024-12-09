

import json
import os
import re


class StateManager:


    def __init__(self, state_path="anicache.json", state=None):
        """Initialize the state manager.
        """
        self.state_path = state_path

        # State is provided
        if state is not None:
            self.state = state
            
        # State should be loaded from file
        else:
            if os.path.exists(state_path):
                self.state = self.load_state(state_path)
            else:
                self.state = self.get_default_state()

    @staticmethod
    def get_default_state():
        """Get the default state.
        """
        return {
            "progress": {},
            "anime": {},
            "errors": [],
            "nonexistent": []
        }

    @staticmethod
    def load_state(state_path):
        """Load the state from a file.
        """
        with open(state_path, "r") as file:
            return json.load(file)

    @staticmethod
    def save_state(state, state_path):
        """Save the state to a file.
        """
        with open(state_path, "w") as file:
            json.dump(state, file, indent=4)

    @staticmethod
    def merge_state(state_path_1, state_path_2):
        """Merge the state with another state.
        """
        state_1 = StateManager.load_state(state_path_1)
        state_2 = StateManager.load_state(state_path_2)

        state_1["progress"].update(state_2["progress"])
        state_1["anime"].update(state_2["anime"])
        state_1["errors"] = list(set(state_1["errors"] + state_2["errors"]))
        state_1["nonexistent"] = list(set(state_1["nonexistent"] + state_2["nonexistent"]))
        
        return state_1

    def search_songs(self, members=None, popularity=None, year=None, rank=None, score=None, song_type="opening"):
        """Search for songs in the state.
        """
        anime_dict = self.state["anime"]

        queries = []
        for mal_id in anime_dict:
            anime = anime_dict[mal_id]

            if members is not None:
                if anime["members"] is None or anime["members"] < members:
                    continue

            if popularity is not None:
                if anime["popularity"] is None or anime["popularity"] > popularity:
                    continue

            if year is not None:
                parsed_years = []
                if anime["aired"] is not None:
                    parsed_years.extend(re.findall(r"\d{4}", anime["aired"]))
                if anime["premiered"] is not None:
                    parsed_years.extend(re.findall(r"\d{4}", anime["premiered"]))
                
                min_year = min(parsed_years) if len(parsed_years) > 0 else None
                if min_year is None or min_year < year:
                    continue

            if rank is not None:
                if anime["rank"] is None or anime["rank"] > rank:
                    continue

            if score is not None:
                if anime["score"] is None or anime["score"] < score:
                    continue

            if song_type == "opening":
                queries.extend([(mal_id, idx) for idx in range(len(anime["openings"]))])
            elif song_type == "ending":
                queries.extend([(mal_id, idx) for idx in range(len(anime["endings"]))])
            else:
                raise ValueError()
            
        return queries

    def query_song(self, mal_id, song_index, song_type="opening"):
        """Query a song in the state.
        """
        anime_dict = self.state["anime"]
        anime = anime_dict[mal_id]

        if song_type == "opening":
            return anime["openings"][song_index]
        elif song_type == "ending":
            return anime["endings"][song_index]

    def query_anime(self, mal_id):
        """Query an anime in the state.
        """
        return self.state["anime"][mal_id]


def main():
    state_manager = StateManager()
    print(state_manager.search_songs(rank=100))

if __name__ == "__main__":
    main()

