import logging
import datetime
import credentials as creds
import tweepy
import schedule
import dateutil
import time
import re
from datetime import datetime

# Authentication for Twitter account
auth = tweepy.OAuthHandler(creds.CONSUMER_KEY, creds.CONSUMER_SECRET, )
auth.set_access_token(creds.ACCESS_TOKEN, creds.ACCESS_TOKEN_SECRET, )
api = tweepy.API(auth)
user = api.me()

print('Authorizing......\nLogging in!')
print(user.name + ' is now authenticated.\n--------------------------------')

logging.basicConfig(filename='logging.txt',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S%p')


def reply_to_reminders():
    """Replies to users who mention the user for a reminder date, with the date requested"""
    print('Searching through mentions for reminder requests\n--------------------------------')
    try:
        # Extended tweet mode is for showing longer tweets in mentions
        mentions = api.mentions_timeline(tweet_mode='extended')
        date_request = re.compile(r"(?:reminder|Reminder)\s\d{2}-\d{2}-\d{4}")
        time_request = re.compile(r"(?i)(?:reminder)\s\d+\s\b(?:seconds?|minutes?|hours?|days?|weeks?|months"
                                  r"?|years?)\b")
        tzinfos = {"UTC"}
        for tweets in reversed(mentions):
            if date_request.search(tweets.full_text):
                logging.info("Found tweet...... MENTION ID: " + str(tweets.id))
                parse_date = dateutil.parser.parse(date_request, dayfirst=False, tzinfos=tzinfos)
                api.update_status(f"@{tweets.user.screen_name} Date Request confirmed."
                                  f"Will remind you of this tweet on the requested date.")
                if parse_date:
                    logging.info("Replying back to tweet......")
                    api.update_status(f"@{tweets.user.screen_name} Here is a reminder about"
                                      f"the tweet you requested.")

            elif time_request.search(tweets.full_text):
                logging.info("Found tweet...... MENTION ID: " + str(tweets.id))
                logging.info("Replying back to tweet......")
                api.update_status(f"@{tweets.user.screen_name} #TimeTestSuccessful")

    except tweepy.RateLimitError:
        api.update_status('Rate limit has been exceeded, 15 min downtime.')
        logging.warning('Rate limit has been exceeded.')
    except tweepy.TweepError:
        logging.error("Status was a duplicate")


def countdown():
    """Daily tweets that update remaining days in the year"""
    try:
        countdown_delta = datetime.datetime(2019, 12, 31,) - datetime.datetime.now()
        api.update_status(str(countdown_delta.days) + ' days ' + 'left in the year')
        final_date = datetime.datetime(2019, 12, 31)

        if final_date:
            api.update_status("Happy New Years!")

    except tweepy.RateLimitError:
        api.update_status('Rate limit has been exceeded, 15 min downtime.')
        logging.warning('Rate limit has been exceeded.')
    except tweepy.TweepError:
        logging.error("Status was a duplicate")


schedule.every().day.at("09:00").do(countdown)


def main():
    while True:
        reply_to_reminders()
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
