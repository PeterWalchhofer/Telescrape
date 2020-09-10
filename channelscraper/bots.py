import selenium
import telethon.tl.types.messages
from urllib.request import Request, urlopen
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
from bs4 import BeautifulSoup
import urllib.request
import traceback
import time
import logging

from client import Client
from driver import Driver
from utilities import concat, eliminateWhitespaces
from message import Message



class Bots:
    client = Client.getClient()
    driver = Driver.getDriver()

    @staticmethod
    def javaScriptLoadMoreHack(url, provider):
        """ All it does is to click on the 'load more comments' button in order to scrape all the messages"""
        if provider == "bot":
            index = 1
            selector = "sg_load"
        else:
            index = 0
            selector = "bc-load-more"
        # use firefox to get page with javascript generated content
        Bots.driver.get(url)
        resultDriver = Bots.loadMore(Bots.driver, index, selector)

        # store it to string variable
        if resultDriver is None:
            return None
        else:
            page_source = resultDriver.page_source
            return BeautifulSoup(page_source, "html.parser")

    @staticmethod
    def loadMore(driver, index, selector):
        """Recursive call of load more if there are lots of comments"""
        selection = driver.find_elements_by_css_selector("." + selector)
        try:
            if len(selection) > index:
                selection[index].click()
            else:
                return None
        except ElementNotInteractableException:
            if (index == 1):
                Bots.loadMore(driver, 0, selector)
            else:
                return None
        # wait for the page to load
        try:
            element = WebDriverWait(driver, 3).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, selector))
            )
            time.sleep(1)
            return driver
        except selenium.common.exceptions.TimeoutException:
            return Bots.loadMore(driver, index, selector)

    @staticmethod
    async def scrapeCommentsApp(url, messageId, queryUser):
        """Scrapes https://comments.app for comment feature extension
        """
        commentList = list()
        userList = list()
        # soup = BeautifulSoup(page, 'html.parser')
        soup = Bots.javaScriptLoadMoreHack(url, "app")
        if soup is None:
            try:
                page = urllib.request.urlopen(url)
                soup = BeautifulSoup(page, "html.parser")
            except Exception:
                logging.info("Exception on loading comments occurred")
                return

        comments = soup.find_all('div', class_='bc-comment-box')
        count = 1  # to create an id for comments, which the naturaly do not have.
        for comment in comments:
            Bots.__parseCommentFromApp(comment, commentList, userList, count, messageId, queryUser)
            count = count + 1

        return commentList, userList


    @staticmethod
    def scrapeCommentsBot(url, channel_users, messageId):
        """ Scrapes https://comments.bot/ website for comment feature extension."""
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://cssspritegenerator.com',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

        soup = Bots.javaScriptLoadMoreHack(url, "bot")
        if soup is None:
            try:
                req = Request(url, headers=hdr)
                page = urlopen(req)
                soup = BeautifulSoup(page, 'html.parser')
            except:
                logging.info("Could not open comments app.")

        commentList = []
        if soup is not None:
            comments = soup.find_all('div', class_='comment-content')
            count = 1
            for comment in comments:
                # Save comment Message
                new_comment = Message()
                new_comment.isComment = True
                new_comment.parent = messageId
                # Save Id
                new_comment.id = str(messageId) + "." + str(count)
                # Save Text
                text_list = comment.find('div', class_='comment-text').contents
                text_list = [elem for elem in text_list if str(elem) != "<br/>"]  # Eliminate Html
                new_comment.text = eliminateWhitespaces(' '.join([str(elem) for elem in text_list]))

                # Save replyId
                reply_text_list = comment.find('span', class_='comment-reply-text')
                if reply_text_list is not None:
                    reply_text = eliminateWhitespaces(' '.join([str(elem) for elem in reply_text_list]))
                    try:
                        new_comment.replyToMessageId = next(
                            (new_comment for new_comment in commentList if new_comment.text ==
                             reply_text), None).id
                    except:
                        logging.info("Could not find quoted comment in Bot: " + url)
                count = count + 1
                # Find not identified User
                new_comment.sender_name = comment.find('div', class_='name-row').findChildren()[0].contents[0]
                commentUser = telethon.types.User(0)
                commentUser.first_name = new_comment.sender_name
                channel_users.append(commentUser)

                new_comment.timestamp = comment.find('div', class_='comment-date').findChildren()[0].contents[0]

                # No identified Users
                commentList.append(new_comment)

        return commentList

    @staticmethod
    def __parseCommentFromApp(comment, commentList, userList, count, messageId, queryUser):
        # Save comment Message
        new_comment = Message()
        new_comment.isComment = True
        new_comment.parent = messageId
        new_comment.id = str(messageId) + "." + str(count)

        # Get all text elements of a comment
        textList = None
        try:
            textList = comment.find_all('div', class_='bc-comment-text')
        except:
            logging.info("This thread has no comments")

        # Save comment text and reply id
        try:
            # Find comment text and quoted comment id.
            if len(textList) > 1:
                try:
                    new_comment.text = textList[1].text
                    new_comment.replyToMessageId = next(
                        (new_comment for new_comment in commentList if new_comment.text ==
                         textList[0].text), None).id
                except AttributeError:
                    logging.info(
                        "Could not find quoted comment" + ", MessageId: " + str(new_comment.id))
            # Find only comment text
            else:
                try:
                    new_comment.text = textList[0].text
                except IndexError:
                    logging.info("Could not find comment text" + ", MessageId: " + str(messageId))

        except:
            traceback.print_exc()
            logging.info("An error occurred reading comment text" + ", MessageId: " + str(messageId))

        # Find not identified User
        new_comment.sender_name = comment.find('span', class_='bc-comment-author-name').contents[0].contents[0]
        # Find identified User and save User ich channel.users and save message.sendername

        try:
            identifierName = comment.find('span', class_='bc-comment-author-name').contents[0]['href'].rsplit('/', 1)[
                -1]
        except:
            identifierName = ""
        user = None

        # Query user if identifier name was found
        if not identifierName == "" and queryUser:
            try:
                user = Bots.getEntity(identifierName)
                userList.append(user)
            except ValueError:
                # User for some reason not found.
                pass

        new_comment.username = identifierName
        if user is not None:
            new_comment.sender_name = concat(user.first_name, user.last_name)
            new_comment.sender = user.id
        else:
            commentUser = telethon.types.User(0)
            commentUser.first_name = new_comment.sender_name

        new_comment.timestamp = comment.find('time')['datetime']
        commentList.append(new_comment)

    @staticmethod
    async def getEntity(identifierName):
        return await Bots.client.get_entity(identifierName)
