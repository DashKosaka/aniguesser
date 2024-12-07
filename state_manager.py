

import json
import os


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
                self.state = self.load_state()
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

    def load_state(self):
        """Load the state from a file.
        """
        with open(self.state_path, "r") as file:
            return json.load(file)

    def save_state(self):
        """Save the state to a file.
        """
        with open(self.state_path, "w") as file:
            json.dump(self.state, file, indent=4)

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

            # if year is None or anime["aired"] < year:
            #     continue

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

