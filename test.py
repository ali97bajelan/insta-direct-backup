# -*- coding: utf-8 -*-

import logging
import urllib
import os
import argparse
import csv
from instagram.instagram import Instagram
from instagram.utils import safe_string


class DirectManager:
    def __init__(self, bot):
        self.bot = bot
        self.threads = dict()
        self.next_page = ''

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

    def get_chat_of_thread(self, thread_title):
        chat = self.bot.direct_thread(self.threads[thread_title])
        person_id = chat['thread']['users'][0]['pk']
        person_username = chat['thread']['users'][0]['username']
        messages = chat['thread']['items']

        text = ''
        for message in messages:
            time = message['timestamp']  # int
            sender_id = message['user_id']  # int
            if sender_id == person_id:
                sender_name = person_username
            else:
                sender_name = "you"
            type = message['item_type']  # str
            if type == "like":
                msg = message['like']
                text += sender_name + "\n"+msg+"\n\n"

            if type == "text":
                msg = message['text']
                text += sender_name + "\n"+msg+"\n\n"

            if type == "profile":
                msg = message['profile']['username']
                text += sender_name + "\n"+"https://www.instagram.com/"+msg+"\n\n"

            if type == "link":
                msg = message['link']['text']
                text += sender_name + "\n"+msg+"\n\n"

        print(text)


bot = Instagram('', '')
bot.login()
direct_manager = DirectManager(bot)
# direct  = bot.direct_list()
# direct_manager.get_all_threads()
direct_manager.find_thread_id("ali.bajelan")
direct_manager.get_chat_of_thread("ali.bajelan")

bot.logout()
