# DEL Bot for DEL Website v5.x.x
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fdiscordextremelist%2Fbot.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fdiscordextremelist%2Fbot?ref=badge_shield)


Licensing information viewable in LICENSE.md

# Setup

## Requirements

### Python 3

Python 3 is required for the DEL bot to function as it is built using python.

**NOTE:** This has only been tested in Python 3.8 and may be broken on newer or older versions of Python 3.

### PM2 (Optional)

PM2 is optional and allows the DEL bot to auto-restart on crash.

### MongoDB

A MongoDB instance is required - it must match the configuration in the `settings.json` file and the values must be the same as the website instance.

## Setup

Install all of the dependencies by running `pip install -r requirements.txt`

## Running

### Without PM2

Run the `python bot.py` command, please note python may be python3 on some platforms.

### With PM2

Run the `pm2 start bot.py --name DEL-BOT` command.


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fdiscordextremelist%2Fbot.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fdiscordextremelist%2Fbot?ref=badge_large)