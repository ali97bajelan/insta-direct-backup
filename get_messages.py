# -*- coding: utf-8 -*-

import logging
import urllib
import os
import argparse
import csv
from instagram.instagram import Instagram
from instagram.utils import safe_string
import datetime


class DirectManager:
    def __init__(self, bot):
        self.bot = bot
        self.threads = dict()
        self.next_page = ''

    def convert_date(self, int):  # int = taken_date
        day = 86400
        d = int // day
        int -= d * day
        zeroDay = datetime.datetime(1970, 1, 1, 3, 30, 0)
        delta = datetime.timedelta(d, int)
        t = zeroDay + delta
        string = str(t)
        date = string[:4] + string[5:7] + string[8:10] + "-" + string[11:].replace(":", "")
        return date

    def get_more_threads(self):
        direct = self.bot.direct_list(next_page=self.next_page)

        if direct:
            items = direct['inbox']['threads']
            for item in items:
                self.threads[item['thread_title']] = item['thread_id']

        if direct['inbox'].get('oldest_cursor'):
            self.next_page = direct['inbox']['oldest_cursor']

        return direct['inbox']['has_older']

    def find_thread_id(self, thread_title):
        while thread_title not in self.threads:
            self.get_more_threads()
        return self.threads[thread_title]

    def get_all_threads(self):
        while self.get_more_threads():
            pass

    def send_direct_item(self, item_type, thread, **options):
        data = {
            'client_context': self.bot.uuid,
            # 'action': 'send_item'
        }

        url = 'direct_v2/threads/broadcast/{}/'.format(item_type)
        text = options.get('text', '')
        text = "in the name of God"
        if item_type == 'link':
            data['link_text'] = text
            data['link_urls'] = self.bot.json.dumps(options.get('urls'))
        elif item_type == 'text':
            data['text'] = text
        elif item_type == 'media_share':
            data['text'] = text
            data['media_type'] = options.get('media_type', 'photo')
            data['media_id'] = options.get('media_id', '')
        elif item_type == 'hashtag':
            data['text'] = text
            data['hashtag'] = options.get('hashtag', '')
        elif item_type == 'profile':
            data['text'] = text
            data['profile_user_id'] = options.get('profile_user_id')
        data['thread_ids'] = thread
        return self.bot.send_request(url, data)

    def get_chat_of_thread(self, thread_title):
        next_page = ''
        text = ''
        while True:
            chat = self.bot.direct_thread(self.threads[thread_title], next_page)
            person_id = chat['thread']['users'][0]['pk']
            person_username = chat['thread']['users'][0]['username']
            messages = chat['thread']['items']

            for message in messages:
                time = message['timestamp']  # int
                time //= 1000000
                time = self.convert_date(time)
                sender_id = message['user_id']  # int
                if sender_id == person_id:
                    sender_name = person_username
                else:
                    sender_name = "You"
                type = message['item_type']  # str
                if type == "like":
                    msg = message['like']
                    text = sender_name + "  " + time + "\n" + msg + "\n\n" + text

                elif type == "media":
                    msg = message['media']['image_versions2']['candidates'][0]['url']
                    text = sender_name + "  " + time + "\n" + msg + "\n\n" + text

                elif type == "media_share":
                    if message['media_share']['media_type'] == 2:
                        msg = message['media_share']['image_versions2']['candidates'][0]['url']
                    if message['media_share']['media_type'] == 8:
                        msg = message['media_share']['carousel_media'][0]['image_versions2']['candidates'][0]['url']
                    text = sender_name + "  " + time + "\n" + msg + "\n\n" + text

                elif type == "text":
                    msg = message['text']
                    text = sender_name + "  " + time + "\n" + msg + "\n\n" + text

                elif type == "reel_share":
                    msg = message['reel_share']['text']
                    text = sender_name + "  " + time + "\n" + "Reply on story: " + msg + "\n\n" + text

                elif type == "story_share":
                    msg = message['story_share']['title']
                    text = sender_name + "  " + time + "\n" + msg + "\n\n" + text

                elif type == "raven_media":
                    pass


                elif type == "profile":
                    msg = message['profile']['username']
                    text = sender_name + "  " + time + "\n" + "https://www.instagram.com/" + msg + "\n\n" + text

                elif type == "link":
                    msg = message['link']['text']
                    text = sender_name + "  " + time + "\n" + msg + "\n\n" + text

                elif type == "placeholder":
                    msg = message['placeholder']['message']
                    text = sender_name + "  " + time + "\n" + msg + "\n\n" + text


                else:
                    print('*******')
                    print(message)
                    print('*******')

            if not chat['thread']['has_older']:
                file = open("backup.txt", "w+", encoding="utf-8")
                file.write(text)
                print(text)
                return

            next_page = chat['thread']['oldest_cursor']


bot = Instagram("username", "password")
bot.login()
direct_manager = DirectManager(bot)
direct_manager.find_thread_id("target_username")
direct_manager.get_chat_of_thread("target_username")
bot.logout()
