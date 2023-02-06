# Capsule Farmer Evolved

Are you tired of watching professional League of Legends games? Do you watch only for the drops? This is a revolution in the farming of League of Legends Esports capsules!

This is a successor to the old [EsportsCapsuleFarmer](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer) which relied on a web browser to watch videos. *Capsule Farmer Evolved* simulates traffic to lolesports.com servers and tricks it into thinking the account is watching a stream. This approach drastically lowers the hardware requirements.

[Learn more about the esports drops directly from Riot games.](https://lolesports.com/article/lol-esports-2022-season-rewards-and-drops-update!/blt4ae38b4643f45741)

### Features
- Watch every live match
- Show how many drops each account received during the program run
- Very lightweight - no external browser needed
- Simple GUI
- 2FA (experimental) - programs prompts for the code on startup
- ARM supported (Raspberry Pi)

### Discord
Share your drops or just come hangout to League of Poro's Discord server: https://discord.gg/c2Qs9Y83hh 

## Installation
1. Download and run the latest CapsuleFarmerEvolved.zip from [Releases tab](https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases/latest)
2. Extract the archive
3. Edit the configuration file `config.yaml` with a text editor (e.g. Notepad) - see [Configuration](#configuration) for details
4. Run `CapsuleFarmer.exe`

There's a [Quickstart guide](https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/wiki/Quickstart-guide) if you have issues

## Configuration
Fill out your username and password in `config.yaml`. Name of the account groups is not important but I recommend entering something recognizable to better detect problems with the account. 
```yaml
accounts:
  accountname:
    username: "username"
    password: "password"
```
You can add as many accounts as you want. _(But be reasonable)_ Example:
```yaml
accounts:
  accountname:
    username: "username"
    password: "password"
  changethistowhatever:
    username: "Riot Poro"
    password: "1234"
```

In case of problem, enable debugging mode to increase verbosity of the log:
`debug: True`

You can select a non-default configuration file, see [CLI](#cli)
```bash
capsulefarmerevolved.exe --config secret.yaml
```

## Notes
- I recommend disabling 2FA on accounts using the bot. It will be way more stable, and it won't ask you for a code in the middle of a random night.
- Not every account receives every drop. That is normal, and it would happen even if you watched it on the web.
![image](https://user-images.githubusercontent.com/95635582/215994461-4f613b76-0e96-4b1a-b138-f1caa748df65.png)
- Regularly check if the "Heartbeat" happened within the last few minutes. If not, restart the program.

## CLI
```
usage: CapsuleFarmerEvolved.exe [-h] [-c CONFIGPATH]

Farm Esports Capsules by watching all matches on lolesports.com.

options:
  -h, --help            show this help message and exit
  -c CONFIGPATH, --config CONFIGPATH
                        Path to a custom config file
```                        
## Installation (advanced)

### Prerequisities
- Python >= 3.10.1 (version 3.9 should work as well but is not officially supported)
- pipenv (`pip install pipenv`)

### Step by step
1. Clone this repo - `git clone https://github.com/LeagueOfPoro/CapsuleFarmerEvolved.git`
2. Move to the directory -  `cd CapsuleFarmerEvolved`
3. Install the Python virtual environment - `pipenv install`
4. Edit the configuration file
5. Run the tool - `pipenv run python ./main.py`

### Update
In the CapsuleFarmerEvolved, run `git pull`

### Create EXE
1.  `pipenv install --dev`
2.  `pipenv run pyinstaller -F --icon=poro.ico ./main.py --collect-all charset_normalizer -n CapsuleFarmerEvolved`

## Docker
Pre-built image:

Edit the `/path/to/config.yaml` to absolute path to your configuration file and run the container in the background:
```
docker run -it --rm --restart unless-stopped --name CapsuleFarmer -d -v /path/to/config.yaml:/config/config.yaml  leagueofporo/capsulefarmer:master
```

If you want to build the image locally:
1. Clone this repo and move to it's direcotry
2. Build the image: `docker build -t capsulefarmerevolved .`
3. Edit the `/path/to/config.yaml` to absolute path to your configuration file and run the container in the background:
```docker
docker run -it --rm --restart unless-stopped -d -v /path/to/config.yaml:/config/config.yaml  capsulefarmerevolved
```

## Support my work
[Subscribe to my channel on YouTube](https://www.youtube.com/channel/UCwgpdTScSd788qILhLnyyyw?sub_confirmation=1) or even

<a href='https://www.youtube.com/channel/UCwgpdTScSd788qILhLnyyyw/join' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://share.leagueofporo.com/yt_member.png' border='0' alt='Become a channel member on YouTube' />
