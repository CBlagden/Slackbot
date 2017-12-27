import time
from requests.sessions import Session
from requests.exceptions import HTTPError
from slacker import Slacker
from threading import Thread
import random
import re
import markovify

short_id = 'G6U7J132N'
tall_id = 'G71E8F0SW'
test_id = 'G767P9MKR'


class MarkovBot:

    def __init__(self):
        text = open('data/data.txt', 'r', encoding='utf-8').read()
        self.text_model = markovify.Text(text)

    def train_bot(self):
        self.__init__()

    def run_bot(self):
        return self.text_model.make_sentence(max_words=25)


class SlackCrawler(Thread):
    def __init__(self, api_key, session, name):
        super(SlackCrawler, self).__init__()
        self.bot = MarkovBot()
        self.name = name
        self._is_running = True
        self.slack = Slacker(api_key, session=session)
        self.ids = []
        for id_group in self.slack.groups.list(exclude_archived=False).body['groups']:
            if id_group['name'] is not 'tall':
                self.ids.append([id_group['id'], False, id_group['name']])
        for id_channel in self.slack.channels.list(exclude_archived=False).body['channels']:
            self.ids.append([id_channel['id'], True, id_channel['name']])

    def post_message(self, mess, channel_name):
        try:
            self.slack.chat.post_message(channel_name, mess)
            time.sleep(8)
        except Exception as err:
            print(err)
            time.sleep(20)
            self.post_message(self.name + ' crashed from ' + str(err), test_id)

    def send_all_emojis(self, channel_name):
        emojis = self.slack.emoji.list().body
        for i in emojis['emoji']:
            self.slack.chat.post_message(channel_name, ':' + i + ':')

    def get_history(self, id, public, count):
        try:
            if public:
                return self.slack.channels.history(id, oldest=0, latest=time.time(), count=count).body['messages']
            else:
                return self.slack.groups.history(id, oldest=0, latest=time.time(), count=count, ).body['messages']
        except HTTPError as err:
            print(err)
            time.sleep(20)
            self.post_message(self.name + ' crashed from ' + str(err), test_id)

    def stop(self):
        self._is_running = False

    def write_data(self, count=1000):
        a = 0
        print('opening file')
        file = open("data.txt", "w", encoding="utf-8")
        for i in self.ids:
            print('writing data')
            for j in self.get_history(i[0], i[1], count):
                file.write(j['text'] + '\n')
                a += 1
        print('closing file')
        file.close()

    def respond_mess(self):
        for id in self.ids:
            history = self.get_history(id[0], id[1], count=1)
            if history is not None:
                for j in history:
                    if 'ping ' + self.name in j['text'] or 'ping all' in j['text']:
                        self.post_message('pong from ' + self.name, id[0])
                        self.post_message(self.bot.run_bot(), id[0])
                        read = True
                        while read:
                            post = False
                            for l in self.get_history(id[0], id[1], count=1):
                                 if post is False:
                                    text = l['text']
                                    print(text)
                                    if 'no_text' not in text:
                                        if self.name + ' --pause' in text:
                                            self.post_message('ending bot ' + self.name, id[0])
                                            read = False
                                        elif '--pause all' in text:
                                            self.post_message('ending bot ' + self.name, id[0])
                                            read = False
                                        elif '--test all' in text:
                                            self.post_message('bot ' + self.name + ' active', id[0])
                                        else:
                                            self.post_message(self.bot.run_bot(text), id[0])
                                            post = True
                                    else:
                                        self.post_message('no text detected', id[0])
                    elif self.name + ' --crawl' in j['text']:
                        self.post_message('training bot ' + self.name, id[0])
                        try:
                            count = int(re.findall('\d+', j['text'])[0])
                        except IndexError as e:
                            print(e)
                            count = 1000
                        self.write_data(count=count)
                        self.bot.train_bot()
                        self.post_message(self.name + ' finished training', id[0])
                    elif self.name + ' --kill' in j['text']:
                        self.post_message('killing bot ' + self.name, id[0])
                        self.stop()
                    elif self.name + ' --test' in j['text']:
                        self.post_message('bot ' + self.name + ' is still running', id[0])
                    elif '--test all' in j['text']:
                        self.post_message('bot ' + self.name + ' active', id[0])
                    elif '--kill all' in j['text']:
                        self.post_message('killing bot ' + self.name, id[0])
                        self.stop()
                        quit()

    def run(self):
        self.post_message(self.name + ' is active', test_id)
        while self._is_running:
            self.respond_mess()
            time.sleep(20)
        quit()
