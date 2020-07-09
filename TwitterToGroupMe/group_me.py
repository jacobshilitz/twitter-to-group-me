import json
import os
import uuid

import requests


class ExceptionGroupMeNotRegistered(Exception):
    """Exception not registerd"""
    pass


class GroupMe:

    def __init__(self, token=None, group_id=None, bot_id=None):

        self.GROUP_ME_API_URL = 'https://api.groupme.com/v3/'
        self.bot_name = os.environ.get('bot_name', '>')
        self.group_name = os.environ.get('group_name', 'Twitter')

        self.groupme_path = 'group_me.json'
        if os.path.exists(self.groupme_path):
            with open(self.groupme_path, 'r') as f:
                data = json.load(f)
                self.token = data.get('token')
                self.params = {'access_token': data.get('token')}
                self.group_id = data.get('group_id')
                self.bot_id = data.get('bot_id')
        else:
            self.token = token
            self.params = {'access_token': token}
            self.group_id = group_id
            self.bot_id = bot_id

        if self.token is None:
            raise ExceptionGroupMeNotRegistered("token is null")

    def create_group(self):
        post_data = {"name": self.group_name}
        res = requests.post(self.GROUP_ME_API_URL + 'groups', json=post_data, params=self.params)
        if res.status_code == 201:
            data = res.json()
            self.group_id = data['response']['group_id']
            return self.group_id
        else:
            return None

    def post_message(self, msg_text):
        post_data = {'message':
                         {"source_guid": str(uuid.uuid4()),
                          "text": msg_text}}
        res = requests.post(f'{self.GROUP_ME_API_URL}groups/{self.group_id}/messages', json=post_data,
                            params=self.params)
        if res.ok:
            return True
        else:
            return res

    def bot_post_message(self, msg_text):
        post_data = {
            "text": msg_text,
            "bot_id": self.bot_id}
        res = requests.post(f'{self.GROUP_ME_API_URL}bots/post', json=post_data,
                            params=self.params)
        if res.ok:
            return True
        else:
            return res

    def create_bot(self, url):
        post_data = {"bot": {'name': self.name,
                             'group_id': self.group_id,
                             'callback_url': url}
                     }
        res = requests.post(f'{self.GROUP_ME_API_URL}bots', json=post_data, params=self.params)
        if res.status_code == 201:
            data = res.json()
            self.bot_id = data['response']['bot']['bot_id']
            return self.bot_id
        else:
            return None

    def save(self):
        with open(self.groupme_path, 'w') as f:
            json.dump({
                'token': self.token,
                'group_id': self.group_id,
                'bot_id': self.bot_id
            }, f)

    def setup(self, url):
        self.create_group()
        self.create_bot(url)
        self.save()


if __name__ == '__main__':
    c = GroupMe()
    c.save()
    print(c.bot_post_message('https://9060cec2f05b.ngrok.io/callback'))

    # c.post_message('TESThgfhh dgdsfs')
    # print(c.create_group())
