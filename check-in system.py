import json
import requests
import os
from dotenv import dotenv_values

script_path = os.path.abspath(os.path.dirname(__file__))
os.chdir(script_path)

api_key = dotenv_values('.env')["aaa"]
video_id = "5g1u4Iya80E"


def load(filename):
    with open(filename, "r", encoding='utf-8') as file:
        return json.load(file)


def save(filename, data):
    with open(filename, "w", encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def chat_id(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=liveStreamingDetails&key={api_key}"
    response = requests.get(url)
    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        live_streaming_details = data["items"][0]["liveStreamingDetails"]
        if "activeLiveChatId" in live_streaming_details:
            return live_streaming_details["activeLiveChatId"]
    return None


def chat_messages(video_id, api_key):
    live_chat_id = chat_id(video_id, api_key)
    if not live_chat_id:
        return []

    url_template = f"https://www.googleapis.com/youtube/v3/liveChat/messages?liveChatId={live_chat_id}&part=snippet,authorDetails&key={api_key}"
    url = url_template
    all_messages = []

    while url:
        response = requests.get(url)
        data = response.json()
        all_messages.extend(data.get("items", []))
        next_page_token = data.get("nextPageToken")
        url = url_template + \
            f"&pageToken={next_page_token}" if next_page_token else None

    return all_messages


def update(video_id, api_key):
    all_audience = load("audience_all.json")
    new_audience = load("audience_new.json")
    messages = chat_messages(video_id, api_key)
    processed_users = set()
    for message in messages:
        username = message['authorDetails']['displayName']
        if username not in processed_users:
            if username not in all_audience:
                all_audience[username] = 1
            else:
                all_audience[username] += 1
            if username not in new_audience:
                new_audience[username] = 1
            else:
                new_audience[username] += 1
            processed_users.add(username)
    save("audience_new.json", new_audience)


update(video_id, api_key)
