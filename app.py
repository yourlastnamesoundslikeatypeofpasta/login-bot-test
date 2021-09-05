import logging
import os

from slack_bolt import App
from slack_sdk.errors import SlackApiError

# start Slack app
# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.ERROR)
logging.basicConfig(level=logging.DEBUG)

try:
    app = App(token=os.environ['bot_token'], signing_secret=os.environ['signin_secret'])
except SlackApiError as e:
    logging.error(e)
