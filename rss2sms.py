# rss2sms.py Takes an RSS feed and sends sms alerts as new items are added to it
# http://github.com/striglia/rss2sms
from twilio.rest import TwilioRestClient
import tinyurl
from subprocess import call
from optparse import OptionParser
import feedparser
import json
import os
import sys

class Rss2Sms():

    def __init__(self, rss_url=None, cell_num=None, cache_filename=None):
        """Initializes cache file and rss feed url, loads last_post from file."""
        if not any([rss_url, cell_num]):
            raise Exception('Must pass rss url and cell number.')
        self.rss_url = str(rss_url)
        self.cell_num = cell_num
        self.cache_filename = str(cache_filename)
        self.from_num = '4088685453'

        # Set up twilio client for sending text messages
        account = os.environ.get('TWILIO_ACCT')
        token = os.environ.get('TWILIO_TOKEN')
        self.twilio_client = TwilioRestClient(account, token)

        self.load_last_post()

    def parse_and_alert(self):
        """Parses self.rss_url and sends alerts for all new posts."""
        self.parse_feed()
        self.alert_new_posts()

    def parse_feed(self):
        """Parses self.rss_url and stores results in self.parsed_feed."""
        parsed_feed = feedparser.parse(self.rss_url)
        # Check for malformed feed
        if parsed_feed['bozo']:
            raise Exception('malformed rss feed!')
        self.parsed_feed = parsed_feed

    def alert_new_posts(self):
        """Compares self.last_post to each item in self.parsed_feed and sends
        alert texts for all new posts, updating self.last_post at the end."""

        for ind, post in enumerate(self.parsed_feed['items']):
            # Record when we match the last-seen post. We will send alerts for
            # all posts occuring after match.
            if not self.is_new_post(post):
                cutoff = ind
                break
        item_list = list(reversed(self.parsed_feed['items'][:ind]))
        if len(item_list) == 0:
            return
        print '%d posts to send alerts for' % len(item_list)
        for post in item_list:
            if self.last_post is None or self.is_new_post(post):
                # Set text body
                tiny_url = tinyurl.create_one(str(post['id']))
                text_body = str(post['title']) + ' - ' + tiny_url
                self.send_sms(text_body)
                print 'Sent text for %s' % tiny_url
            break
        self.set_last_post(post)

    def send_sms(self, body):
        """Sends an sms to all numbers in self.sms_numbers with body as the content."""
        message = self.twilio_client.sms.messages.create(to=self.to_num, from_=self.from_num, body=body)

    def is_new_post(self, post):
        """Compares post id with self.last_post for equality."""
        return self.last_post != post['id']

    def load_last_post(self):
        """Tries to load the last post from file."""
        if os.path.exists(self.cache_filename):
            with open(self.cache_filename,'r') as cache_file:
                self.last_post = json.load(cache_file)
        else:
            self.last_post = None

    def set_last_post(self, post):
        """Saves the last seen post to file."""
        with open(self.cache_filename,'w') as cache_file:
            json.dump(post['id'], cache_file)

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="rss_url",
                            help="url of rss feed")
    parser.add_option("-c", "--cell-num", dest="cell_num",
                            help="cell number to send sms alerts to")
    parser.add_option("-f", "--cache-filename", dest="cache_filename",
                            help="optional file to cache last post in")

    (options, args) = parser.parse_args()
    rss2sms = Rss2Sms(**vars(options))
    rss2sms.parse_and_alert()
