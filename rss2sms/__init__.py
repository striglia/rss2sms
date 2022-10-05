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
import time
import calendar


__version__ = '0.0.1'

class Rss2Sms():

    def __init__(self, rss_url=None, to_num=None, cache_filename=None, from_num=None, rss_id_field=None, rss_display_field=None):
        """Initializes cache file and rss feed url, loads last_post from file."""
        if not rss_id_field:
            rss_id_field = 'link'
        if not rss_display_field:
            rss_display_field = 'title'
        if not from_num:
            from_num = os.environ.get('TWILIO_NUMBER')

        if not any([rss_url, to_num, from_num]):
            raise Exception('Must pass rss url (-u), from-number (-f) and to number (-t).')
        self.rss_url = str(rss_url)
        self.cache_filename = str(cache_filename)
        self.from_num = from_num
        self.to_num = to_num
        self.rss_id_field = rss_id_field
        self.rss_display_field = rss_display_field

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

        cutoff = len(self.parsed_feed['items'])
        for ind, post in enumerate(self.parsed_feed['items']):
            # Record when we match the last-seen post. We will send alerts for
            # all posts occuring after match.
            if not self.is_new_post(post):
                cutoff = ind
                break
        item_list = list(reversed(self.parsed_feed['items'][:cutoff]))
        if len(item_list) == 0:
            return
        print '%d posts to send alerts for' % len(item_list)
        for post in item_list:
            if self.last_post is None or self.is_new_post(post):
                # Set text body
                url = str(post[self.rss_id_field])
                text_body = u' '.join((post[self.rss_display_field], url)).encode('utf-8').strip()
                self.send_sms(text_body)
                print 'Sent text for %s' % tiny_url
            break
        self.set_last_post(post)

    def send_sms(self, body):
        """Sends an sms to all numbers in self.sms_numbers with body as the content."""
        message = self.twilio_client.sms.messages.create(to=self.to_num, from_=self.from_num, body=body)

    def is_new_post(self, post):
        """Compares post id with self.last_post for equality, and also timestamp."""
        return self.last_post != post[self.rss_id_field] and self.last_timestamp < self.get_post_timestamp(post)

    def load_last_post(self):
        """Tries to load the last post and its timestamp from file."""
        if os.path.exists(self.cache_filename):
            with open(self.cache_filename,'r') as cache_file:
                s = json.load(cache_file)
                self.last_timestamp = s[0]
                self.last_post = s[1].encode('utf-8')
        else:
            self.last_post = None
            self.last_timestamp = 0

    def set_last_post(self, post):
        """Saves the last seen post to file together with its timestamp."""
        with open(self.cache_filename,'w') as cache_file:
            json.dump([self.get_post_timestamp(post),post[self.rss_id_field]], cache_file)

    def get_post_timestamp(self, post):
        updated = post['updated_parsed']
        return calendar.timegm(updated)

def main():
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="rss_url",
                            help="url of rss feed")
    parser.add_option("-t", "--to", dest="to_num",
                            help="cell number to send sms alerts to")
    parser.add_option("-f", "--from", dest="from_num",
                            help="cell number to send sms alerts to (overrides environment variable TWILIO_NUMBER)")
    parser.add_option("-i", "--id", dest="rss_id_field",
                            help="unique id rss field used for display in SMS and for equality comparison (defaults to 'link')")
    parser.add_option("-d", "--display", dest="rss_display_field",
                            help="name of rss field used for display in SMS (defaults to 'title')")
    parser.add_option("-c", "--cache-filename", dest="cache_filename",
                            help="optional file to cache last post in")

    (options, args) = parser.parse_args()
    rss2sms = Rss2Sms(**vars(options))
    rss2sms.parse_and_alert()
