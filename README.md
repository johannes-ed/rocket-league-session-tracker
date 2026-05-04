# RLSessionTracker - Play Session Tracker for Rocket League

<img width="340" height="225" alt="image" src="https://github.com/user-attachments/assets/adec770c-2c79-4c98-b96c-9393758ae51c" />

A simple app that displays current Rocket League play session stats: wins, losses, streak etc. The data is read from the new local game API.  
Tries to recreate the functionality of the old RocketStats-plugin from when BakkesMod worked.

## How to use

- Download the zip file from [releases](https://github.com/johannes-ed/rocket-league-session-tracker/releases), extract and launch the RLSessionTracker.exe. 

- The app reads data from the built-in game API which is not activated by default. To enable it, follow the instructions in the official documentation: https://www.rocketleague.com/en/developer/stats-api  
In summary, edit the "\<Install Dir>\TAGame\Config\DefaultStatsAPI.ini" file and set the PacketSendRate value to at least 1.  
To absolutely guarantee that all information is registered in the app in time, a PacketSendRate of at least 10 is recommended, but 1 is fine. 

- If the app manages to connect to the game, the small dot in the corner will be green instead of red.

- The rest should be automatic, it will show the stats from the last played playlist unless you hit the toggle playlist button. You can only toggle between playlists that have been played this session.

## Features/Quirks

- Displays number of wins, losses and current streak for each played game mode during a session.

- Stores each win/loss/streak for each playlist and allows toggling between them.

- Auto-detects which game mode/playlist you are playing. But cannot differentiate between casual/ranked.

- Allows leaving before the last overtime replay is over or as soon as a forfeit happens. In these cases, the win/loss is based on the current standings. So if you abandon/crash while in the lead, it will count as a win.

- It will register games that are active while the app is started.

- No data is stored, when closing the app everything is reset. But the game can be restarted and the stats kept. 

- It cannot overlay on top of a full screen game unfortunately.
