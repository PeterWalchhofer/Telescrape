import re
from random import random
from datetime import datetime, timedelta
import asyncio
import os
import telethon
import logging


def getInputPath():
    path = os.path.dirname(os.path.dirname(__file__)) + "/input"
    create_path_if_not_exists(path)
    return path


def getOutputPath():
    path = os.path.dirname(os.path.dirname(__file__)) + "/output"
    create_path_if_not_exists(path)
    return path


def concat(first_name, last_name):
    if first_name is None:
        first_name = ""
    if last_name is None:
        last_name = ""
    return first_name + " " + last_name


def eliminateWhitespaces(text):
    return re.sub(r"\s\s+", " ", text)


def calcDateOffset(offset):
    if offset <= 0:
        raise AttributeError("Offset must be greater 0")
    return datetime.now() - timedelta(days=offset)


async def wait():
    """ Random sleep time to avoid getting blocked by telegram."""
    randomNum = random() / 10
    if randomNum < 0.0001:
        await asyncio.sleep(3)
    await asyncio.sleep(randomNum)


def create_path_if_not_exists(channelPath):
    if not os.path.exists(channelPath):
        os.makedirs(channelPath)


def extractUrls(message):
    """ Url extraction by RegEx and telegram url entity to get maximum results"""
    urls_regex = re.findall(r"(?P<url>https?://[^\s]+)", message.text)
    # if found through regex add it, if not already found (because it has bugs)
    for i in range(len(urls_regex)):
        url_reg = urls_regex[i]
        match = re.search(r".jpg|.htm|.html|.mp4", url_reg)
        if match is not None:
            urls_regex[i] = url_reg[0:match.end()]

    entities = message.entities
    if entities is None:
        return urls_regex
    urls = []

    for entity in entities:
        if type(entity) == telethon.tl.types.MessageEntityUrl:
            try:
                enc_text = message.text.encode('utf-16-le')
                url = enc_text[entity.offset * 2:(entity.offset + entity.length) * 2].decode('utf-16-le')
                if (re.match("http|www", url)):
                    urls.append(url)
            except UnicodeDecodeError:
                logging.info("Unicode Error for text")
                pass

    for url in urls:
        for url_reg in urls_regex:
            if url in url_reg:
                urls_regex.remove(url_reg)

    urls.extend(urls_regex)
    list(dict.fromkeys(urls))  # remove duplicates
    return urls


def getClassName(object):
    if object is not None:
        return object.__name__
    else:
        return ""
