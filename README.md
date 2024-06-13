# VGS_bot_2
A Discord bot created for the VGS, a French shiny hunting competition taking place on Pokémon games. This bot has been designed to help the hosts of the competition by automating repetitive tasks that had to be done by hand before, leading to errors and complaints.

The first version of the bot was released in 2023 for the 7th edition of the VGS and prove to be very helpful by saving a lot of time and preventing a lot of management issues that were common before. This second version will be launched for the 2024 edition and has been entirely rewritten to enhance its base functionalities, fix the issues that were encountered as well as implementing new commands.

## Features
- Keeping track of inventories, missions and quests of all the teams taking part in the competition, as well as displaying the corresponding information on a dedicated channel updated with updates in real-time.
- Managing all the items that can be earned and used by the participants with their gold variants, as well as the effects resulting from their use.
- Keeping track of each team's gimmick list, allowing the hosts to update the status of each gimmick and to use items impacting the gimmicks
- Managing multiple commands used in parallel, allowing the bot to be used simultaneously by all the teams.

## Installation
The bot requires Python version 3.10 or greater to run. You can verify your Python version by running the following command in a terminal:
```
python3 --version
```

Download the source code and open a terminal in the root directory of the project.

If you want, you can create and activate a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```

When you want to leave your environment, simply run the command:
```
deactivate
```

To install the required packages, run the following command:
```
python3 -m pip install -r requirements.txt
```

If you need to upgrade pip, you can run:
```
python3 -m pip install --upgrade pip
```

If everything is set up correctly, the bot can be started by using the command:
```
python3 main.py
```

## Changelog
| <b>Version | <b>Release date | <b>Changes                |
|------------|-----------------|---------------------------|
| <b>1.2     | 2024-06-08      | Missions                  |
| <b>1.1     | 2024-05-30      | Gimmicks and Clairvoyance |
| <b>1.0     | 2024-05-20      | Basic item functionality  |

## Contributors
- [Yoyovicti](https://github.com/Yoyovicti)

## Upcoming features
- History of previous commands
- Backup of inventories
- Alerting of bosses and teams in a separate channel
- Points calculator
- Small useful commands for participants
- Remove Herobrine
- Full competition management, including points and leaderboard
- Statistics