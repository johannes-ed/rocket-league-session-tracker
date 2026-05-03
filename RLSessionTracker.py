import sys
import signal

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from JSONObjectTCPReader import JSONObjectTCPReader

class RLSessionTracker(QObject):
    """Session tracker for rocket league, takes data in the form of json objects from RL game API."""
    
    current_playlist_updated = Signal(str)
    session_stats_updated = Signal(dict)
    
    def __init__(self, debug_mode: bool=False):
        super().__init__()
        self.debug_mode = debug_mode
        
        self._reset_match_values()
        self._just_launched = True # only true if the match values have never been reset, it is to allow saving match results from a match that had already began when program was launched.

        # this is the dictionary that will containand store all the current session data from each played playlist.
        self.session_stats = {}

    def _reset_match_values(self):
        # all the variables that help in determining game mode, winner, etc.
        self._just_launched = False
        self._initialized_guid = None
        self._initialized_match = False
        self._in_replay = False
        self._in_overtime = False
        self._current_standings = [0, 0]
        self._current_team = None
        self._players_in_team = [0, 0]
        self._current_playlist = None



    def handle_message(self, msg: dict):
        """Function that should be called from a TCP stream reader that sends a finished JSON message object and handles it."""
        
        event = msg.get('Event')
        data = msg.get('Data')

        # no handling for match created for now because it seems like the guid value is broken, the field is empty
        if event == 'UpdateState':
            self._handle_update_state(data)
        if event == 'MatchCreated':
            self._handle_match_created(data)
        elif event == 'MatchInitialized':
            self._handle_match_initialized(data)
        elif event == 'MatchDestroyed':
            self._handle_match_destroyed(data)
        elif event == 'MatchEnded':
            self._handle_match_ended(data)

    def _handle_match_created(self, match_created_data: dict):
        # for some reason, the match created guid was empty when tested before so it is only collected when the match initializes instead.
        
        self._reset_match_values() # when a match is created, all values are reset. This also happens at initialize but is needed here too so that the get_target_team does not run while in choose team menu through the _just_launced system.

    def _handle_match_initialized(self, match_init_data: dict):
        init_guid = match_init_data.get('MatchGuid')

        if init_guid: # check if the guid actually has any value, launching freeplay for example does call this initialize function but with no guid
            self._reset_match_values() # reset all match values for clean slate when new game starts
            
            self._initialized_guid = init_guid # stores guid to compare when match is ended or destroyed to verify that the game was in order
            self._initialized_match = True # indicates that a match has been initialized and is active

            if self.debug_mode: print(f"[TRACKER] Match initialized. Stats:\n{self.session_stats}")

    def _handle_update_state(self, update_state_data: dict):
        guid = update_state_data.get('MatchGuid')
        self._in_replay = update_state_data.get('Game').get('bReplay')
        self._in_overtime = update_state_data.get('Game').get('bOvertime')

        if self._initialized_match: 
            if self._in_replay != True:
                self._current_team = self._get_target_team(update_state_data) # if we are NOT in a replay and in an active match, check what team the target (active player) is in. This throws error if in replay because no target player. 
            self._current_playlist = self._get_current_playlist(update_state_data) # continuously update playlist while in game checking if more players join and adjusts accordingly. If players leave, the playlist stays at the highest number.
            self._current_standings = self._get_current_standings(update_state_data) # current standings are needed if the match is destroyed to see if it should count as a win. 
        elif self._just_launched and guid: # if the program was just launched, and we are in a game, allow saving the results without guid verification
            self._initialized_guid = guid
            self._initialized_match = True
            self._just_launched = False
        
        if self.debug_mode: print(f"[TRACKER] Match updated and active. {update_state_data}")

    def _handle_match_destroyed(self, match_destroyed_data: dict):
        if self._initialized_match and self._initialized_guid == match_destroyed_data.get('MatchGuid'): # checks that match is active/initialized and that the Guid:s match, that guid check might not be needed but in case there is some way for things to break it is a backup.
            stats = self.session_stats.setdefault(self._current_playlist, {'Wins': 0, 'Losses': 0})
            
            if self._current_standings[self._current_team] > self._current_standings[1-self._current_team]: # if target player is in the lead, count as win if the match is destroyed. This does mean that if a player leaves before overtime win or forfeit (i.e. abandons, crashes etc.) the game will count as a win.
                stats['Wins'] += 1
            else: 
                stats['Losses'] += 1

            self.current_playlist_updated.emit(self._current_playlist)
            self.session_stats_updated.emit(self.session_stats) # emit updated session data to GUI
        
        # if above if statement is not true, something is broken and the match data won't count
        self._reset_match_values()

        if self.debug_mode: print(f"[TRACKER] Match destroyed. Stats:\n{self.session_stats}")

    def _handle_match_ended(self, match_ended_data: dict):
        if self._initialized_match and self._initialized_guid == match_ended_data.get('MatchGuid'):
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

    def _get_current_standings(self, update_state_data: dict) -> bool:
        game = update_state_data.get('Game')
        teams = game.get('Teams')

        standings = [0, 0]
        for team in teams:
            team_num = team.get('TeamNum')
            team_score = team.get('Score')
            standings[team_num] = team_score

        return standings

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
