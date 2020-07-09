import os

from flask import request

from TwitterToGroupMe import app, log
from TwitterToGroupMe.group_me import GroupMe, ExceptionGroupMeNotRegistered
from TwitterToGroupMe.twitter import Twitter
import re

twitter = None
try:
    group_me = GroupMe()
except ExceptionGroupMeNotRegistered:
    group_me = None

if group_me:
    try:
        twitter = Twitter(group_me.bot_post_message)
        twitter.run()
    except:
        twitter = None


@app.route('/')
def start():
    auth_url = os.environ.get('auth_url')
    if not group_me:
        return '<a href="{}">CLick here to connect your account</a>'.format(auth_url)
    else:
        return 'bot is running!'


@app.route('/auth')
def auth():
    global group_me
    token = request.args.get('access_token')
    # create_group(token)
    group_me = GroupMe(token)
    group_me.setup()
    return 'Done Please check your text'


@app.route('/callback', methods=['POST'])
def callback():
    text = request.json.get('text')
    log.info(text)
    # https://regex101.com/r/W5UX7Q/1
    pattern = re.compile(r'^follow\s(.*)')
    m = re.search(pattern, text)

    if m:
        names = m.group(1)
        log.info(names)
        res = twitter.follow(names)

        if res:
            group_me.bot_post_message("Success!! You are now following:\n{}".format('\n'.join(names.split())))

    return 'ok'


if __name__ == '__main__':
    app.run()
