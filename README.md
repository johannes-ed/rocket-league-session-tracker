# RLSessionTracker - Play Session Tracker for Rocket League

A simple app that displays current Rocket League play session stats: wins, losses, streak etc. The data is read from the new local game API. 

## How to use

- Download the zip file from [releases](https://github.com/johannes-ed/rocket-league-session-tracker/releases), extract and launch the RLSessionTracker.exe. 

- The app reads data from the built-in game API which is not activated by default. To enable it, follow the instructions in the official documentation: https://www.rocketleague.com/en/developer/stats-api  
In summary, edit the "\<Install Dir>\TAGame\Config\DefaultStatsAPI.ini" file and set the PacketSendRate value to at least 1.  
To absolutely guarantee that all information is registered in the app in time, a PacketSendRate of at least 10 is recommended, but 1 is fine. 

- If the app manages to connect to the game, the small dot in the corner will be green instead of red. 

## Features/Quirks

## Planned additions

- Button to manually toggle between which playlist stats are being shown instead of just the latest played game mode.
