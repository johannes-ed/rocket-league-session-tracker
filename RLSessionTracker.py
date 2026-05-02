import sys
import signal

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from JSONObjectTCPReader import JSONObjectTCPReader

class RLSessionTracker(QObject):
    """Session tracker for rocket league, takes data in the form of json objects in rl game api."""
    
    current_playlist_updated = Signal(str)
    session_stats_updated = Signal(dict)
    
    def __init__(self, debug_mode: bool=False):
        super().__init__()
        self.debug_mode = debug_mode
        
        self._reset_match_values()

        # this is the dictionary that will containand store all the current session data from each played playlist.
        self.session_stats = {}

    def _reset_match_values(self):
        # these are used to make sure that each match is separated and no results get mixed up
        self._initialized_guid = None
        self._active_match = False

        # these are used at the end of each match to update session stats correctly
        self._current_team = None
        self._players_in_team = [0, 0]
        self._current_playlist = None



    def handle_message(self, msg: dict):
        event = msg.get('Event')
        data = msg.get('Data')

        # no handling for match created for now because it seems like the guid value is broken, the field is empty
        if event == 'UpdateState':
            self._handle_update_state(data)
        elif event == 'MatchInitialized':
            self._handle_match_initialized(data)
        elif event == 'MatchEnded':
            self._handle_match_ended(data)

    def _handle_match_initialized(self, match_init_data: dict):
        init_guid = match_init_data.get('MatchGuid')

        if init_guid: # check if the guid actually has any value, launching freeplay for example does initialize but with no guid
            self._reset_match_values()
            
            self._initialized_guid = init_guid
            self._active_match = True

            if self.debug_mode: print(f"[TRACKER] Match initialized. Stats:\n{self.session_stats}")

    def _handle_update_state(self, update_state_data: dict):
        in_replay = update_state_data.get('Game').get('bReplay')
        
        if self._active_match and in_replay != True:
            self._current_team = self._get_target_team(update_state_data)
            self._current_playlist = self._get_current_playlist(update_state_data)

            if self.debug_mode: print(f"[TRACKER] Match updated and active. {update_state_data}")

    def _handle_match_ended(self, match_ended_data: dict):
        if self._active_match and self._initialized_guid == match_ended_data.get('MatchGuid'):
            stats = self.session_stats.setdefault(self._current_playlist, {'Wins': 0, 'Losses': 0})
            
            winner_team_num = match_ended_data.get('WinnerTeamNum')
            if self._current_team == winner_team_num:
                stats['Wins'] += 1
            else: 
                stats['Losses'] += 1

            self.current_playlist_updated.emit(self._current_playlist)
            self.session_stats_updated.emit(self.session_stats) # emit updated session data to GUI
        
        # if above if statement is not true, something is broken and the match data won't count
        self._reset_match_values()

        if self.debug_mode: print(f"[TRACKER] Match ended. Stats:\n{self.session_stats}")



    def _get_target_team(self, update_state_data: dict) -> int:
        """Takes UpdateState message data and returns the team of the target player."""
        
        game = update_state_data.get("Game")

        target = game.get('Target')
        return target.get('TeamNum')

    def _get_current_playlist(self, update_state_data: dict) -> str:
        """Decodes current playlist based on numbers of players on each team as well as the asset name of the current map."""

        players = update_state_data.get('Players')

        players_in_team = [0, 0]
        for p in players: # only players active in game should be listed with a player entry, not spectators?
            team_num = p.get('TeamNum')
            players_in_team[team_num] += 1

        # Update the numbers of players in teams only if the max count has increased this game. A 2v2 match when one player leaves should still count as 2v2 for example.
        if players_in_team[0] > self._players_in_team[0] or players_in_team[1] > self._players_in_team[1]: self._players_in_team = players_in_team 

        # kind of get the current game mode based on asset name of current map, very unreliable though and only works for few game modes. The rest become default soccar.
        arena_label = update_state_data.get('Game').get('Arena').lower()
        if 'hoop' in arena_label:
            game_mode = 'Hoops'
        elif 'shatter' in arena_label:
            game_mode = 'Dropshot'
        elif 'snow' in arena_label:
            game_mode = 'Snow Day'
        else:
            game_mode = 'Soccar'

        return f'{self._players_in_team[self._current_team]}v{self._players_in_team[1-self._current_team]} {game_mode}'

def main():
    app = QApplication(sys.argv)
    
    tcp = JSONObjectTCPReader()
    rl_tracker = RLSessionTracker(debug_mode=True)

    tcp.message_received.connect(rl_tracker.handle_message)
    
    rl_tracker.session_stats_updated.connect(lambda obj: print(f"[TRACKER] Emitted object received:\n{obj}"))

    tcp.start()

    signal.signal(signal.SIGINT, signal.SIG_DFL) # This might not work, it is just to be able to stop the app from python console
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
