import asyncio
import csv
import logging
import os
import time
import traceback
from datetime import datetime

import telethon.tl.types.messages
from bots import Bots
from client import Client
from config import Config
from message import Message
from utilities import concat, wait, calcDateOffset, getOutputPath, create_path_if_not_exists, extractUrls


class Channel:
    config = Config.getConfig()
    client = Client.getClient()
    logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                        level=logging.INFO)

    def __init__(self, link, isBroadcastingChannel):
        self.id = None

        self.users = list()
        if isBroadcastingChannel == "True":
            self.isBroadcastingChannel = True
        else:
            self.isBroadcastingChannel = False
        self.username = link.rsplit('/', 1)[-1]

        self.path = getOutputPath() + "/" + self.username
        self.messages = list()

    def scrape(self):
        create_path_if_not_exists(self.path)

        if Channel.config.get("scrape_mode") == "OFFSET_SCRAPE":
            self.getRecentChannelMessages()
        elif Channel.config.get("scrape_mode") == "FULL_SCRAPE":
            self.getAllChannelMessages()
        else:
            raise AttributeError("Invalid scraping mode set in config file.")

    # Collects messages and comments from a given channel.
    def getRecentChannelMessages(self):
        """ Scrapes messages of a channel of the last X days and saves the information in the channel object.
        """

        async def main():
            async for message in Channel.client.iter_messages(self.username, offset_date=calcDateOffset(
                    Channel.config.get("scrape_offset")), reverse=True):
                if type(message) == telethon.tl.types.Message:
                    await self.parseMessage(message)

        with Channel.client:
            try:
                Channel.client.loop.run_until_complete(main())
            except telethon.errors.ServerError:
                logging.info("Server error: Passed")
                pass
            except telethon.errors.FloodWaitError as e:
                logging.info("FloodWaitError: Sleep for " + str(e.seconds))
                time.sleep(e.seconds)

        self.messages = list(reversed(self.messages))

    # Collects messages and comments from a given channel.
    def getAllChannelMessages(self):
        """ Scrapes all messages of a channel and saves the information in the channel object.
        """

        async def main():
            async for message in Channel.client.iter_messages(self.username):
                if type(message) == telethon.tl.types.Message:
                    await self.parseMessage(message)

        with Channel.client:
            try:
                Channel.client.loop.run_until_complete(main())
            except telethon.errors.ServerError:
                logging.info("Server error: Passed")
                pass
            except telethon.errors.FloodWaitError as e:
                logging.info("FloodWaitError: Sleep for " + str(e.seconds))
                time.sleep(e.seconds)

    async def parseMessage(self, message):
        # Wait to prevent getting blocked
        await wait()

        new_message = Message()
        new_message.id = message.id
        new_message.sender = message.sender_id
        try:
            first_name = message.sender.first_name
            last_name = message.sender.last_name
        except AttributeError:
            first_name = ""
            last_name = ""
        new_message.sender_name = concat(first_name, last_name)
        try:
            new_message.username = message.sender.username
        except AttributeError:
            pass
        new_message.replyToMessageId = message.reply_to_msg_id
        new_message.edit_date = message.edit_date
        new_message.entities = message.entities
        new_message.post_author = message.post_author
        new_message.timestamp = message.date
        new_message.text = message.text
        new_message.views = message.views
        new_message.media = type(message.media)
        self.member_count = message.chat.participants_count

        # Saves the channel from which the message was forwarded.
        try:
            await self.__parseForward(message, new_message)
        except AttributeError:
            pass

        if type(message.media) == telethon.types.MessageMediaPhoto and Channel.config.get("media_download"):
            mediapath = self.path + "/media/" + str(new_message.id)
            if not os.path.exists(mediapath + ".jpg"):
                try:
                    await message.download_media(mediapath)
                except telethon.errors.FloodWaitError as e:
                    logging.info("Waiting " + str(e.seconds) + " seconds: FloodWaitError")
                    await asyncio.sleep(e.seconds)
                except telethon.errors.RpcCallFailError:
                    pass
                await asyncio.sleep(1)

        # Checks which kind of comment bot is used by the provider of the group a uses the correct scraper.
        #   --> then fills the comment list for each messages with the comments (prints "no comments" if no comment
        #   bot is used.
        comments = list()
        if message.buttons is not None and message.forward is None:
            buttons = message.buttons

            for button in buttons:
                button_url = None
                try:
                    button_url = button[0].button.url[:21]
                except AttributeError:
                    pass

                if button_url == 'https://comments.bot/':
                    logging.info("---> Found comments.bot...")
                    new_message.hasComments = True
                    new_message.bot_url = button[0].button.url
                    try:
                        comments.extend(Bots.scrapeCommentsBot(new_message.bot_url, self.users, message.id))
                    except Exception:
                        traceback.print_exc()
                elif button[0].text[-8:] == 'comments':
                    logging.info("---> Found comments.app...")
                    new_message.hasComments = True
                    new_message.bot_url = button[0].button.url
                    try:
                        commentsAppComments, commentsAppUsers = \
                            await Bots.scrapeCommentsApp(new_message.bot_url, message.id,
                                                         Channel.config.get("query_users"))
                        comments.extend(commentsAppComments)
                        self.users.extend(commentsAppUsers)
                    except Exception:
                        traceback.print_exc()

            new_message.comments = comments
        self.messages.append(new_message)

    def writeCsv(self):
        if len(self.messages) == 0:
            raise LookupError("Nothing to write. You have to execute 'scrape' method first.")

        chatlogs_csv = self.path + "/chatlogs_" + str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S")) + ".csv"
        users_csv = self.path + "/users" + str(datetime.now().strftime("%Y-%m-%d--%H-%M-%S")) + ".csv"

        # WRITE MESSAGES AND COMMENTS
        with open(chatlogs_csv, "w", encoding="utf-8", newline='') as chatFile:
            writer = csv.writer(chatFile)
            writer.writerow(Message.getMessageHeader())
            for message in self.messages:
                message.urls = extractUrls(message)
                writer.writerow(message.getMessageRow(self.username, self.member_count, self.isBroadcastingChannel))

                for comment in message.comments:
                    comment.urls = extractUrls(comment)
                    writer.writerow(comment.getMessageRow(self.username, self.member_count, self.isBroadcastingChannel))

        with open(users_csv, "w", encoding="utf-8", newline='') as users_csv:
            writer = csv.writer(users_csv)
            writer.writerow(Message.getUserHeader())
            for user in self.users:
                # Write in user table.
                writer.writerow(
                    [self.username, user.id, user.first_name, user.last_name, concat(user.first_name, user.last_name),
                     user.phone, user.bot, user.verified, user.username])

    async def __parseForward(self, message, new_message):
        if message.forward is not None:
            if message.forward.chat is not None:
                new_message.forward = message.forward.chat.username
                new_message.forwardId = message.forward.chat.id
                if new_message.forwardId is None:
                    new_message.forwardId = message.forward.channel_id
            elif message.forward.sender is not None:
                sender = message.forward.sender
                new_message.forward = concat(sender.first_name, sender.last_name)
                new_message.forwardId = sender.id
            else:
                new_message.forward = "Unknown"
                new_message.forwardId = "Unknown"

            if message.forward.original_fwd is not None:
                new_message.forward_msg_id = message.forward.original_fwd.channel_post
                new_message.forward_msg_date = message.forward.date

    def getChannelUsers(self):
        """ Scrape the users of a channel, if it is not a broadcasting channel."""
        if self.isBroadcastingChannel:
            return

        async def main():
            async for user in Channel.client.iter_participants(self.username, aggressive=True):
                if type(user) == telethon.types.User:
                    if user not in self.users:
                        self.users.append(user)

        with Channel.client:
            try:
                Channel.client.loop.run_until_complete(main())
            except telethon.errors.FloodWaitError as e:
                print("FloodWaitError: Sleep for " + str(e.seconds))
                time.sleep(e.seconds)
