# rss2sms

Takes an RSS feed and sends sms alerts as new items are added to it

## Usage

Usage: rss2sms [options]

    Options:
      -h, --help            show this help message and exit
      -u RSS_URL, --url=RSS_URL
                            url of rss feed
      -t TO_NUM, --to=TO_NUM
                            cell number to send sms alerts to
      -f FROM_NUM, --from=FROM_NUM
                            cell number to send sms alerts to (overrides
                            environment variable TWILIO_NUMBER)
      -i RSS_ID_FIELD, --id=RSS_ID_FIELD
                            unique id rss field used for display in SMS and for
                            equality comparison (defaults to 'link')
      -d RSS_DISPLAY_FIELD, --display=RSS_DISPLAY_FIELD
                            name of rss field used for display in SMS (defaults to
                            'title')
      -c CACHE_FILENAME, --cache-filename=CACHE_FILENAME
                            optional file to cache last post in

## Setup

1. First, you need to setup an account with www.Twilio.com and get an SMS number
2. Add the number to the env.variable `TWILIO_NUMBER`
3. Add your Twilio account id to the env.variable `TWILIO_ACCT`
4. Add your Twilio token to the env.variable `TWILIO_TOKEN`

You also need to obtain the URL to an RSS/Atom feed that you want to monitor

## Examples

    rss2sms --url="http://my.site.com/rss-feed" --to=+4712345678 -c mycache.txt
    
    #Enter from-number on the cmdline:
    rss2sms --url="http://my.site.com/rss-feed" --to=+4712345678 --from=+198765443 -c mycache.txt
    
    # Send another RSS field than the title
    rss2sms --url="http://my.site.com/rss-feed" --to=+4712345678 --display=link
    
    # If your RSS uses another field name for the URL than 'link':
    rss2sms --url="http://my.site.com/rss-feed" --to=+4712345678 --id=id
