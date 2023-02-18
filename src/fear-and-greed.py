import fear_and_greed
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

fgx = fear_and_greed.get()

channel_id = "#알림"
message = f"SPX sentiment: {fgx.description} ({round(fgx.value, 2)})" 
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
                                                
                                                
try:
    # Initialize a Slack WebClient instance with the bot token
    client = WebClient(token=SLACK_BOT_TOKEN)

    response = client.chat_postMessage(
        channel=channel_id,
        text=message,
    )
    thread_ts = response["ts"]

except SlackApiError as e:
    print("Error uploading file to Slack: {}".format(e))
