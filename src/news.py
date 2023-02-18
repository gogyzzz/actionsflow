#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
from time import sleep

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import time
import datetime

# In[212]:

newspaper_name = "매경"
url = 'https://media.naver.com/press/009/newspaper'
pattern = r'^https://n\.news\.naver\.com/article/newspaper/009/'

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})

# Replace with the name of the channel to send the message to
CHANNEL_NAME = "#알림"

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

NUM_ARTICLES = 2

# In[111]:


def get_article_links(url, pattern):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    a_tags = soup.find_all('a', href=True)
    links = list(filter(lambda t: re.match(pattern, t) ,[tag['href'] for tag in a_tags]))
    return links


# In[215]:


def get_content(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_link = f'<a href="{url}">{url}</a><br/><br/>'
    head_div = soup.find_all('h2', {'id': 'title_area'})
    divs = soup.find_all('div', {'id': 'dic_area'})

    def remove_html_tags(text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def replace_br_tags(text):
        return text.replace('<br/>', '\n').replace('\n\n', '\n')
    if len(divs) > 0:
#         replaced = replace_br_tags(f"{url}\n\n{head_div[0]}\n{divs[0]}")
#         removed = remove_html_tags(replaced)
#         return removed
        return f"{article_link}\n\n{head_div[0]}\n{divs[0]}"
    else:
        return None


# In[113]:


def get_all_contents(links):
    all_contents = []
    for l in links:
        content = get_content(l)
        if content:
            all_contents.append(content)
            sleep(1)
    return all_contents


# In[218]:


def write_file(contents, filename):
    with open(filename, 'w', encoding='utf-8') as f:
#         f.write(sep.join(contents))
        f.write('\n'.join(contents))


# In[184]:


def upload_to_slack(filename):
    try:
        # Initialize a Slack WebClient instance with the bot token
        client = WebClient(token=SLACK_BOT_TOKEN)

        # Call the chat_postMessage API method using the WebClient
        response = client.files_upload(
            channels=CHANNEL_NAME,
            file=filename,
            filetype='text'
        )


        print(f"File uploaded to Slack: {response['file']['permalink']}")

    except SlackApiError as e:
        print("Error uploading file to Slack: {}".format(e))



def job():
    print("Function running at", datetime.datetime.now())
    links = get_article_links(url, pattern)
    contents = get_all_contents(links[:NUM_ARTICLES])

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the current date as a string
    date_string = now.strftime("%Y-%m-%d")
    filepath = f'{newspaper_name}_{date_string}.html'
    write_file(contents, filename=filepath)
    # message_to_slack()
    upload_to_slack(filepath)

job()
