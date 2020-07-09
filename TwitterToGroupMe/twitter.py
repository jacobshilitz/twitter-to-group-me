import json
import os

import tweepy
from tweepy import TweepError
from unidecode import unidecode

from TwitterToGroupMe import log


class MainTwitterStreamer(tweepy.StreamListener):

    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback

    def on_status(self, tweet):

        if hasattr(tweet, "retweeted_status"):  # Check if Retweet
            log.info("skip retweet")
        else:
            text = f"{tweet.user.screen_name} : {unidecode(tweet.status.full_text)}"

            log.info('tweet %s', text)

            if self.callback:
                self.callback(text)


class Twitter:

    def __init__(self, callback):

        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(os.environ.get("consumer_key"), os.environ.get("consumer_secret"))
        auth.set_access_token(os.environ.get("access_token"), os.environ.get("access_token_secret"))

        self.following_path = 'following.json'
        if os.path.exists(self.following_path):
            with open(self.following_path, 'r') as f:
                self.following = json.load(f)
        else:
            self.following = {}

        self.stream = None
        self.callback = callback
        self.api = tweepy.API(auth)

        try:
            self.api.verify_credentials()
            log.info('logged in twiiter')
        except:
            log.warning("Error during authentication")

    def get_users_id(self, names):
        log.info('getting %s', names)
        user_objects = self.api.lookup_users(screen_names=names)
        user_ids = [user.id_str for user in user_objects]

        for user in user_objects:
            if user.id_str in self.following.items():
                print('user_ids already following')
            else:
                self.following[user.screen_name] = user.id_str

        with open(self.following_path, 'w') as f:
            json.dump(self.following, f)

        return user_ids

    def follow(self, names):
        self.stop_stream()
        ids = self.get_users_id(names.split())
        log.info('new ids followingnow %s', ids)
        self.start_stream()
        if len(ids) >= 1:
            return True
        else:
            return False

    def stop_stream(self):
        if self.stream:
            log.info('quiting twitter stream')
            self.stream.disconnect()

    def start_stream(self):
        follow_list = [user for user in self.following.values()]
        log.info('streaming %s', follow_list)
        twitter_stream_listener = MainTwitterStreamer(self.callback)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=twitter_stream_listener)
        self.stream.filter(follow=follow_list, is_async=True)

    def run(self):
        try:
            log.info('starting')
            self.start_stream()
        except Exception as e:
            log.info('', exc_info=e)
        # finally:
        #     log.info('quiting')
            # self.stop_stream()


    # api = tweepy.API(auth)
    #
    # try:
    #     api.verify_credentials()
    #     print('loged in')
    # except:
    #     print("Error during authentication")
    #
    # def get_id(names):
    #     user_objects = api.lookup_users(screen_names=names)
    #     user_ids = [user.id_str for user in user_objects]


if __name__ == '__main__':
    t = Twitter()
    t.follow('JacobPython')

# # Create API object
#
# def send_tweet(text):
#     api = tweepy.API(auth, wait_on_rate_limit=True,
#                      wait_on_rate_limit_notify=True)
#     try:
#         api.update_status(text)
#     except TweepError as e:
#         print(f'Tweepy error {e}')
#
#     print("posted to twitter")
