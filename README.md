# Capsule Farmer Evolved

Are you tired of watching professional League of Legends games? Do you watch only for the drops? This is an revolution in farming of League of Legends Esports capsules!

**NO WEB BROWSER NEEDED!** The old [EsportsCapsuleFarmer](https://github.com/LeagueOfPoro/EsportsCapsuleFarmer) relied on a web browser to watch videos. *Capsule Farmer Evolved* simulates traffic to lolesports.com servers and tricks it into thinking the account is watching a stream. This approach drastically lowers the hardware requirements.

### Features
- Automatically logs user in
- Watches every live match
- Lightweight
- No web browser needed

## Installation
1. Download and run the latest CapsuleFarmerEvolved.zip from [Releases tab](https://github.com/LeagueOfPoro/CapsuleFarmerEvolved/releases)
2. Extract the archive
3. Edit the configuration file `config.yaml` with a text editor (e.g. Notepad) - see [Configuration](#configuration) for details
4. Run `CapsuleFarmer.exe`
5. If you do not use the autologin feature - log into your account 

## Configuration
Fill out your username and password in `config.yaml`. Name of the account groups is not important but I recommend entering something recognizable to better detect problems with the account. 
```yaml
accounts:
  accountname:
    username: "username"
    password: "password"
  anotheraccountname:
    username: "username"
    password: "password"
debug: True
```

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
4. (Optional) Edit the configuration file
5. Run the tool - `pipenv run python ./main.py`

### Update
In the CapsuleFarmerEvolved, run `git pull`

### Create EXE
1.  `pipenv install --dev`
2.  `pipenv run pyinstaller -F --icon=poro.ico ./main.py --collect-all charset_normalizer -n CapsuleFarmerEvolved`

## Docker
If you want to build image locally:
1. Clone this repo and move to it's direcotry
2. Build the image: `docker build -t capsulefarmerevolved .`
3. Edit the `/path/to/config.yaml` to absolute path to your configuration file and run the container in the background:
```docker
docker run -it --rm -d -v /path/to/config.yam:/config/config.yaml  capsulefarmerevolved
```

## Known Issues
- 2FA is not supported
