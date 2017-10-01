import time
from requests.sessions import Session
from requests.exceptions import HTTPError
from slacker import Slacker
from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
from threading import Thread
import random
import re

api_key_trinity_corp = 'xoxp-190294483460-190341461781-243885747221-95d8dc8567cd2cd79ec4050e8e1047ee'
api_key_3309 = 'xoxp-3278486248-78952291655-243217296100-1016975c2c9f1f22db6c6a9af2100cdc'
short_id = 'G6U7J132N'
tall_id = 'G71E8F0SW'
test_id = 'G767P9MKR'
lines = [line.rstrip('\n') for line in open('data.txt', 'r', encoding='utf-8')]


class Bot:
    def __init__(self):
        self.bot = ChatBot('Liz',
                           storage_adapter='chatterbot.storage.SQLStorageAdapter',
                           input_adapter='chatterbot.input.VariableInputTypeAdapter',
                           output_adapter='chatterbot.output.OutputAdapter',
                           logic_adapters=[
                               'chatterbot.logic.BestMatch',
                           ],
                           filters=[
                               'chatterbot.filters.RepetitiveResponseFilter'
                           ],
                           database='./database.sqlite3')

    def train_bot(self):
        self.bot.set_trainer(ListTrainer)
        lines = [line.rstrip('\n') for line in open('data.txt', 'r', encoding='utf-8')]
        self.bot.train(lines)

    def run_bot(self, user_input):
        try:
            return self.bot.get_response(user_input)
        except(KeyboardInterrupt, EOFError, SystemExit):
            return 'Exception, bot interrupted'


class SlackCrawler(Thread):
    def __init__(self, api_key, session, name):
        super(SlackCrawler, self).__init__()
        self.bot = Bot()
        self.name = name
        self._is_running = True
        self.slack = Slacker(api_key, session=session)
        self.ids = []
        for id_group in self.slack.groups.list(exclude_archived=False).body['groups']:
            if id_group['name'] is not 'tall':
                self.ids.append([id_group['id'], False, id_group['name']])
        for id_channel in self.slack.channels.list(exclude_archived=False).body['channels']:
            self.ids.append([id_channel['id'], True, id_group['name']])

    def post_message(self, mess, channel_name):
        try:
            self.slack.chat.post_message(channel_name, mess)
            time.sleep(8)
        except Exception as err:
            print(err)
            time.sleep(20)
            self.post_message(self.name + ' crashed from ' + str(err), test_id)
            self.post_message(random.choice(lines), channel_name)

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

    def write_data(self, count=50):
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
                        self.post_message(random.choice(lines), id[0])
                        read = True
                        while read:
                            post = False
                            for l in self.get_history(id[0], id[1], count=1):
                                 if post is False:
                                    text = l['text']
                                    print(text)
                                    if 'no_text' not in text:
                                        if '--pause ' + self.name in text:
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
                    elif '--crawl ' + self.name in j['text']:
                        self.post_message('training bot ' + self.name, id[0])
                        self.write_data(count=int(re.findall('\d+', j['text'])[0]))
                        self.bot.train_bot()
                        self.post_message(self.name + ' finished training', id[0])
                    elif '--spawn' in j['text']:
                        with Session() as sess:
                            name = str(j['text']).strip('--spawn ')
                            new_bot = SlackCrawler(api_key_3309, sess, name)
                            new_bot.post_message('new bot active from ' + name, id[0])
                            new_bot.start()
                    elif '--kill ' + self.name in j['text']:
                        self.post_message('killing bot ' + self.name, id[0])
                        self.stop()
                    elif '--test ' + self.name in j['text']:
                        self.post_message('bot ' + self.name + ' is still running', id[0])
                    elif '--test all' in j['text']:
                        self.post_message('bot ' + self.name + ' active', id[0])
                    elif '--kill all' in j['text']:
                        self.post_message('killing bot ' + self.name, id[0])
                        self.stop()
                        quit()
                    else:
                        pass

    def run(self):
        while self._is_running:
            self.respond_mess()
            time.sleep(20)
        quit()


if __name__ == '__main__':
    with Session() as session:
        s = SlackCrawler(api_key_3309, session, name='liz')
        s.start()