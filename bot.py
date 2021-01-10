import asyncio
import logging
import sys

import discord
import yaml
from discord.ext import commands
from twilio.rest import Client

config = yaml.safe_load(open("config.yml"))
bot = commands.Bot(command_prefix=config["prefix"], intents=discord.Intents.default())
logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)


def create_embed(message: discord.Message, status: str, colour: int) -> discord.Embed:
    """
    Creates an embed based on the specified params.
    :param message: discord.Message object to extract content from
    :param status: Status to use in title, e.g. 'pending, dispatched, timed out'
    :param colour: Hex code to use for embed colour
    :return: discord.Embed
    """
    embed = discord.Embed(
        title=f"Urgent Notification ({status})",
        description=f"Your alert has been set to {status.lower()}.",
        colour=colour,
    )

    embed.add_field(name="Messsage", value=message.clean_content, inline=False)

    if status.lower() == "pending":
        embed.add_field(
            name="Actions",
            value="Please react with \N{MOBILE PHONE} to dispatch a notification.",
            inline=False,
        )
    return embed


def make_call(message: discord.Message) -> None:
    """
    Initiates a call based on Twilio configuration
    :param message: Message to read out after initial message
    :return: Log message confirming call SID
    """
    client = Client(config["account_sid"], config["auth_token"])

    for number in config["numbers"]:
        logging.info(f"Calling {number} with message {message.clean_content}")

        call = client.calls.create(
            twiml=f"<Response>"
            f"<Say>"
            f"{config['initial_message']} {message.clean_content}"
            f"</Say>"
            f"</Response>",
            to=number,
            from_=config["number_from"],
        )

        logging.info(f"Initiated call with SID {call.sid}")


@bot.event
async def on_message(message: discord.Message) -> None:
    """Triggers a pending call when message is posted in alert channel"""
    if message.author.bot:
        return

    channel = bot.get_channel(config["alert_channel"])

    if message.channel.id == channel.id:
        pending = await channel.send(embed=create_embed(message, "Pending", 0xFF0000))
        await pending.add_reaction("\N{MOBILE PHONE}")
        logging.info(f"Pending message has been created by {message.author}")

        def valid_reactions(user_reaction, member) -> bool:
            """Checks requirements for dispatching a call"""
            return (
                user_reaction.message.id == pending.id
                and str(user_reaction.emoji) == "\N{MOBILE PHONE}"
                and not member.bot
            )

        try:
            author = await bot.wait_for(
                "reaction_add", check=valid_reactions, timeout=config["timeout"]
            )
        except asyncio.TimeoutError:
            await pending.edit(embed=create_embed(message, "Timed out", 0x000000))
            await pending.remove_reaction("\N{MOBILE PHONE}", bot.user)
            return await pending.add_reaction("\N{CROSS MARK}")

        await pending.edit(embed=create_embed(message, "Dispatched", 0x88FF00))
        make_call(message)
        logging.info(f"Pending message has been dispatched by {author}")


if __name__ == "__main__":
    bot.run(config["token"])
