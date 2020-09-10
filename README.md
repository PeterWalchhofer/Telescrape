# Telegram Scraper

This is Telegram scraper designed to help journalists collect telegram messages. It was originally build for this [story](https://www.addendum.org/news/telegram-netzwerk-sellner/).
## Setup

### Requirements:
- Google Chrome
- Python 3
- Telegram Account (Phone Number)
- A lot of storage if downloading media. 
- Time - arround 3000msg and comments/ per Minute.

### Getting Started 

1. Install dependencies `make install`
2. Create your own `channel.csv` as explained in
3. Put the phone-number of the linked telegram account int the `config.yaml`
4. Get your Api Keys [here](https://my.telegram.org/auth?to=apps) an put the im the `config.yaml`.
5. `sh scrape.sh` to start the scraper 
6. The outputs will be stored in the `/output` directory. 


### Input Data 
You need to create your own `channels.csv`and put it in the `/input` folder. 

Only **Link** and **Broadcast** Relevant for scrpaing. The csv should have the form described below. There also is an example csv in the folder.

Kategorie | Name | **Link** | @ | **Broadcast**
--- | --- | --- | --- | --- 
Gruppe Typ XY | Example Channel | https://t.me/example_channel | example_channel | TRUE

* Kategorie(optional): Metadata to annotate channel
* Name(optional): Not identifier Name
* Link: Link to channel
* @ (optional): Indentifier Name
* Broadcast: True if channel is Broadcasting Channel else false 

### Configuration 

The Scraper can be further configured via the `channelscraper/config.yaml`.

## Features 
### Messages 
The Scraper extracts alle messages from a channel.

### Comment Bots
- In vielen Broadcasting-Channels wird eine Kommentarfunktion mittels Bot hinzugefügt, diese werden von uns ebenso gescraped.
- Comments Bot hat ein anderes Timestamp Format (z.B. Dec 09)
- "Load more comments" wird mittels Selenium geklickt (deswegen ist auch der Treiber nötig, dieser sollte automatisch erkannt werden)
  wichtig ist Google Chrome Version 79 zu haben.
#### Comments.app
- Hier funktioniert die User extraction bei vielen Nutzern. Damit wird die ID gespeichert. Das geht nicht bei allen Nutzern (sind möglicherweise gelöscht) 
- Wir primät von Sellner benutzt
#### Comments.bot
- Keine User extraction
- Anzeigename wird gespeichert und reicht vielleicht auch für die Identifizierung aus.

## Entitäten
### User 
- Hat immer eine ID, außer er wurde aus Kommentar extrahiert UND konnte nicht gefunden werden
- first + lastname = der anzeigename der in Telegram angezeigt wird
### Message
- Message oder Kommentar
- ReplyToId ist die ID der Nachricht auf die diese Nachricht antwortet -> Dies gilt auch für Kommentare!
- Links werden gespechert
  - Links in diesem Format sind eigentlich Telegram Medien "https://telegra.ph/file/153021558fa33f50bbdcf.mp4"


## Deployment

Für Ausführung mit Chrome in Docker-Image `selenium/standalone-chrome:3.141.59-yttrium`

Siehe auch:
https://stackoverflow.com/questions/45323271/how-to-run-selenium-with-chrome-in-docker
