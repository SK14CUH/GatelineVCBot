# Auto-Voice-Channels (Adam's Gateline Edit)

### A Discord bot that automatically creates voice channels as they are needed.

## Requires:

* [Python 3.7+](https://www.python.org/downloads/)
* [discord.py](https://pypi.org/project/discord.py/) (`pip install discord.py`)
* [pytz](https://pypi.org/project/pytz/) (`pip install pytz`)
* [psutil](https://pypi.org/project/psutil/) (`pip install psutil`)
* [Requests](https://pypi.org/project/requests/) (`pip install requests`)

## Optional Extras:

* [uvloop](https://pypi.org/project/uvloop/) (`pip install uvloop`) - **UNIX ONLY**

## Quick start:

### On Linux (Ubuntu/Debian):

* Go to the directory containing the bot's python scripts.
* Install pip: `sudo apt-get -y install python3-pip`
* Install venv: `pip3 install virtualenv`
* Make venv: `python3 -m virtualenv bot-env`
* Use venv: `. bot-env/bin/activate`
* Install requirements: `python3 -m pip install -r requirements.txt`
* Create your application + bot here: <https://discordapp.com/developers/applications>
* Enable both **Presence** and **Server Members** Privileged Gateway Intents in the Bot section.
* Create a `config.json` file in the bot's folder and fill it in:
  * `admin_id` is your personal [user ID](https://techswift.org/2020/04/22/how-to-find-your-user-id-on-discord/), for the bot to DM you errors and other important logs.
  * `client_id` is the bot application client ID.
  * `log_timezone` is for the time displayed in logs, see [this list](https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones).
  * `token` is your bot's private token you can find [here](https://discordapp.com/developers/applications) - do not share it with anyone else.
  * There are a number of [optional settings](https://wiki.dotsbots.com/en/self-hosting/optional-config) too, which aren't necessary to set but provide some further configuration options if needed.
  * Your `config.json` file should look something like this:

```json
{
    "admin_id":123456789012345678,
    "client_id":987654321098765432,
    "log_timezone":"Africa/Johannesburg",
    "token":"XXXXXXXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

* Invite the bot to your own server, replacing `<YOUR BOT ID>` with... your bot ID: `https://discordapp.com/api/oauth2/authorize?client_id=<YOUR BOT ID>&permissions=286280784&scope=bot`
* Start your bot: `python3 auto-voice-channels.py`

### On Windows:

While this bot will work just fine on windows for development, the most likely reason you've scrolled here is because you want to run your bot on your home computer.

This is **not recommended** for two main reasons:

1. Your internet connection is probably less stable than you think, which means high & inconsistent latency with frequent disconnects of your bot.
2. Your bot would only be online while your computer is on, meaning no one could use it while you sleep - and if you're thinking about running your home computer 24/7, consider that you'll be spending **a lot** more on electricity than a simple hosted VPS or Raspberry Pi would cost you.

Our recommended solution for "free" hosting is to use the free credit provided by many of the cloud platforms (e.g. Google Cloud). Once the credit expires after a few months, if you're still using your bot regularly you probably won't mind paying $3-5 per month for a tiny VPS.

If you absolutely want to run this bot on windows (e.g. for development testing), simply follow the instructions for Linux above, and anywhere you need to use `apt-get`, just search up how to install that software on windows instead :)

### With Docker:

If you want to use Docker, here's an image: https://github.com/vinanrra/Auto-Voice-Channels-Docker
