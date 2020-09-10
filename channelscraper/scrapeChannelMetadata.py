import time

import telethon
import os
import yaml
import csv
from client import Client
import traceback
from channel import Channel
from telethon.tl.functions.channels import GetFullChannelRequest
from utilities import getInputPath, getOutputPath
from driver import Driver


def getChannelList(filename):
    """Initialises the CSV of channels to scrape given by ADDENDUM."""
    channelList = []
    with open(getInputPath() + '/' + filename, newline='',
              encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        csvList = list(reader)
        for row in csvList[1:]:
            channelList.append(row[2].split("/")[-1])
    return channelList

client = Client.getClient()
config = yaml.safe_load(open("config.yaml"))
input_file = config["input_channel_file"]
channels = getChannelList(input_file)

channel_info_list = list()
i = 1
for channel in channels:
    i = i + 1
    print("Channel: " + channel + " Nr: " + str(i))
    time.sleep(3)
    try:
        channel_entity = client.get_entity(channel)
        channel_full_info = client(GetFullChannelRequest(channel=channel_entity))

        if channel_full_info.full_chat.location is not None:
            geo_point = channel_full_info.full_chat.location.geo_point
            address = channel_full_info.full_chat.location.address
        else:
            geo_point = ""
            address = ""
        channel_info_list.append(
            [channel_entity.username, channel_entity.id, channel_full_info.full_chat.about, channel_entity.broadcast,
             channel_entity.date, channel_full_info.full_chat.participants_count, geo_point
                , address])
    except:
        traceback.print_exc()
        channelExists = False
        print("Channel '" + channel + "' does not exist.")

with open(getInputPath() + '/' + '/channel_info.csv', mode="w",
          newline='',
          encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["channel", "id", "about", "broadcast", "created_at", "members", "location", "address"])
    for channel in channel_info_list:
        writer.writerow(channel)

Driver.closeDriver()
