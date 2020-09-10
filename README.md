# Telegram Scraper

This Telegram scraper collects telegram messages, comments (comments.bot/comments.app) and media files. It was originally build for this [story](https://www.addendum.org/news/telegram-netzwerk-sellner/) on behalf of [Addendum](https://addendum.org).
## Setup

### Requirements:
- Google Chrome (However, in theory you could als use Firefox when installing the necessary driver manually )
- Python 3
- Telegram Account (Phone Number)
- A lot of storage if downloading media
- Time - arround 3000msg and comments/ per Minute.

### Getting Started 

1. Install dependencies `make install` OR just install requirements.txt (using venv is recommended)
2. Create your own `channel.csv` as explained in the next section
3. Put the phone-number of the linked telegram account int the `config.yaml`
4. Get your API-key [here](https://my.telegram.org/auth?to=apps) an put them inside the `config.yaml`.
5. `sh scrape.sh` to start the scraper OR run `channelscraper/python app.py`
6. The outputs will be stored in the `/output` directory. 


### Input Data 
You need to create your own `channels.csv`and put it in the `/input` folder. 

Only **Link** and **Broadcast** Relevant for scraping. The csv should have the form described below. There also is an example csv in the folder.

Kategorie | Name | **Link** | @ | **Broadcast**
--- | --- | --- | --- | --- 
Gruppe Typ XY | Example Channel | https://t.me/example_channel | example_channel | TRUE

* Kategorie(optional): Metadata to annotate channel
* Name(optional): Not identifier Name
* Link: Link to channel
* @ (optional): Indentifier Name
* Broadcast: ´True´ if channel is Broadcasting Channel ´else´ false. Broadcasting channels are large one-to-many channels that only allow owners to write messages.

### Configuration 

The Scraper can be further configured via the `channelscraper/config.yaml`.

## Features 
### Messages 
The Scraper extracts all messages from a channel. It is also possible to scrape only those messages that were written in the last x days. This can be set in the `config.yaml`.

### Comment Bots
- In many broadcasting channels comment-bots are used in order to provide feedback from the audience. It is also possible to scrape those messages. Currently comments.app and comments.bot bots are supported.
- Be careful. The date format is different from the telegram-api and has to be parsed manually (e.g. Dec 09)
- As there is a "Load more comments" button it has to be clicked using javascript. Selenium is used to interact with the chrome driver that is installed automatically.
#### Comments.app
- Unique username extraction is working most of the time. However, if the user has deleted its account, this is not possible.
#### Comments.bot
- Unique usernames are not extracted, because we found no way to find out without querying the api at a high cost.
- Only the display name is persited

## Further remarks
- Messages and comments are persisted in the same csv-file. To tell them apart use the `isComment` column. Additionally, the ID includes a period in the format msgId.commId (e.g. 101.3)
- We allocated ids to the comments manually. The telegram message ids are unique within a channel.

## Optional

If you want to run selenium with docker use `selenium/standalone-chrome:3.141.59-yttrium`
Also see:
https://stackoverflow.com/questions/45323271/how-to-run-selenium-with-chrome-in-docker
