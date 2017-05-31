# Verkehrsbot
Telegram bot for DVB/VVO departures.

You can talk to this bot via [@verkehr_bot](https://telegram.me/verkehr_bot) on Telegram.

## Usage

Send your location to the bot to get a list of the closest five stations as a custom keyboard. Select one and you will get the next departures. You can also send `/Abfahrten Station [#]` to get the departures at Station (optionally in # minutes).

## Caveats

As the bot is currently hosted on Microsoft Azure, it needs some helper scripts and a precompiled Python wheel for pyproj. When my Azure subscription runs out, I might switch to a different provider or deactivate the bot.

## Licenses

* Verkehrsbot Copyright (c) 2017 dirko (MIT license)
* deploy.cmd Copyright (c) 2016 Kevin Kuszyk (MIT license)
* pyproj copyright (c) 2013 by Jeffrey Whitaker. (ISC license)
* Azure Python helper scripts (app.py, ptvs_virtualenv_proxy.py) Copyright (c) Microsoft Corporation. (Apache License 2.0)
* Stations list from https://github.com/kiliankoe/vvo
