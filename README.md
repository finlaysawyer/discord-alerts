# Discord Alerts

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Discord Alerts is a Discord bot that allows you to dispatch text-to-speech phone calls from a text channel.
The original use case was to allow users to make an automated emergency phone call out of hours.
The Twilio library is used to make phone calls, see the config for requried params.

## Installation
The bot requires Python 3.6+, and is built and tested against 3.7.

1. Install Requirements: `pip install -r requirements.txt`
2. Rename `config.example.yml` to `config.yml` and configure as you desire.

## Usage
A user sends a message in the `alert_channel`:
- If the user reacts with a `mobile phone` emoji, the call will be dispatched
- If the user does not react within the `timeout` time, the call will be voided