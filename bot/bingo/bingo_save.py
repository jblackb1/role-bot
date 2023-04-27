import os
import pickle

class GameSave:
    def __init__(self, save_file="../game_save.pkl"):
        self.save_file = save_file

        # If the save file exists, load the game data
        if os.path.exists(self.save_file):
            self.load()
        else:
            # Initialize game data
            self.selections = {}
            self.game_state = 0
            self.winners = []
            self.current_board = []

    def save(self):
        game_data = {
            "selections": self.selections,
            "game_state": self.game_state,
            "winners": self.winners,
            "current_board": self.current_board
        }
        with open(self.save_file, 'wb') as f:
            pickle.dump(game_data, f)

    def load(self):
        with open(self.save_file, 'rb') as f:
            loaded_game_data = pickle.load(f)
        self.selections = loaded_game_data["selections"]
        self.game_state = loaded_game_data["game_state"]
        self.winners = loaded_game_data["winners"]
        self.current_board = loaded_game_data["current_board"]

    def reset(self):
        self.selections = {}
        self.game_state = 0
        self.winners = []
        self.current_board = []
        self.save()

    def save_attr(self, selections=None, game_state=None, winners=None, current_board=None):
        if selections is not None:
            member_id = list(selections.keys())[0]
            if member_id in self.selections:
                self.selections[member_id].update(selections[member_id])
            else:
                self.selections.update(selections)

        if game_state is not None:
            self.game_state = game_state

        if winners is not None:
            for winner in winners:
                if winner not in self.winners:
                    self.winners.append(winner)

        if current_board is not None:
            self.current_board = current_board

        self.save()