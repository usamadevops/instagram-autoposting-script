import os
import time
import requests
from instagrapi import Client
from instagrapi.types import Usertag, Location
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

load_dotenv()

Username = os.environ.get("IG_USERNAME")
Password = os.environ.get("IG_PASSWORD")
targetUrl = os.environ.get("TARGET_USERNAME")
databaseUrl = os.environ.get("DATABASE_URL")

def login(username, password):
    print("Logging in...")
    client = Client()
    client.login(username, password)
    print(f"Login successful for user: {username}")
    return client

def fetch_latest_post(client, target_username, posted_shortcodes):
    print(f"Fetching a post from {target_username}...")
    user_id = client.user_id_from_username(target_username)
    user_media = client.user_medias(user_id, amount=20)

    for media in user_media:
        media_shortcode = media.code
        if media_shortcode in posted_shortcodes:
            continue

        media_details = client.media_info(media.pk)
        caption = media_details.caption_text

        if media_details.media_type == 1:  # Photo
            media_type = "photo"
            image_url = media_details.thumbnail_url
            resources = None
            video_url = None
            thumbnail_url = None
        elif media_details.media_type == 2:  # Video, Reel, or IGTV
            product_type = media_details.product_type
            if product_type == "feed":
                media_type = "video"
            elif product_type == "igtv":
                media_type = "igtv"
            elif product_type == "clips":
                media_type = "reel"
            else:
                continue
            video_url = media_details.video_url
            thumbnail_url = media_details.thumbnail_url
            resources = None
        elif media_details.media_type == 8:  # Carousel (Album)
            media_type = "album"
            resources = media_details.resources
            image_url = None
            video_url = None
            thumbnail_url = None
        else:
            continue

        return media_type, image_url, video_url, thumbnail_url, resources, caption,media_shortcode

    print(f"No suitable post found for {target_username}")
    return None, None, None, None, None, None

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def photo_upload(client, path: Path, caption: str, usertags: List[Usertag] = [], location: Location = None, extra_data: Dict = {}):
    media = client.photo_upload(path, caption, usertags=usertags, location=location, extra_data=extra_data)
    return media

def video_upload(client, path: Path, caption: str, thumbnail: Path, usertags: List[Usertag] = [], location: Location = None, extra_data: Dict = {}):
    media = client.video_upload(path, caption, thumbnail, usertags=usertags, location=location, extra_data=extra_data)
    return media

def album_upload(client, paths: List[Path], caption: str, usertags: List[Usertag] = [], location: Location = None, extra_data: Dict = {}):
    media = client.album_upload(paths, caption, usertags=usertags, location=location, extra_data=extra_data)
    return media

def igtv_upload(client, path: Path, title: str, caption: str, thumbnail: Path, usertags: List[Usertag] = [], location: Location = None, extra_data: Dict = {}):
    media = client.igtv_upload(path, title, caption, thumbnail, usertags=usertags, location=location, extra_data=extra_data)
    return media

def clip_upload(client, path: Path, caption: str, thumbnail: Path, usertags: List[Usertag] = [], location: Location = None, extra_data: Dict = {}):
    media = client.clip_upload(path, caption, thumbnail, usertags=usertags, location=location, extra_data=extra_data)
    return media

# Load Firebase credentials from the JSON key file
firebase_credentials = credentials.Certificate("service-account-key.json")

# Initialize the Firebase app
firebase_app = firebase_admin.initialize_app(firebase_credentials, {
    'databaseURL': databaseUrl
})

# Get a reference to the posted_media_ids node in the database
posted_shortcodes_ref = db.reference('posted_shortcodes')

def main():
    username = Username or os.environ["IG_USERNAME"]
    password = Password or os.environ["IG_PASSWORD"]
    target_username = targetUrl
    interval = 60 * 1  # Post every hour

    client = login(username, password)

    # Load posted media IDs from Firebase Realtime Database or create an empty list
    posted_shortcodes = posted_shortcodes_ref.get() or []

    while True:
        try:
            media_type, image_url, video_url, thumbnail_url, resources, caption,media_shortcode = fetch_latest_post(client, target_username,posted_shortcodes)

            if media_type == "photo":
                filename = f"{target_username}_latest_post.jpg"
                download_file(image_url, filename)
                media = photo_upload(client, filename, caption)
            elif media_type == "video" or media_type == "reel" or media_type == "igtv":
                video_filename = f"{target_username}_latest_post.mp4"
                thumbnail_filename = f"{target_username}_latest_post_thumbnail.jpg"
                download_file(video_url, video_filename)
                download_file(thumbnail_url, thumbnail_filename)
                if media_type == "video":
                    media = video_upload(client, video_filename, caption, thumbnail_filename)
                elif media_type == "reel":
                    media = clip_upload(client, video_filename, caption, thumbnail_filename)
                else:
                    media = igtv_upload(client, video_filename, caption, caption, thumbnail_filename)
            elif media_type == "album":
                paths = []
                for i, resource in enumerate(resources):
                    if resource.media_type == 1:
                        ext = '.jpg'
                        url = resource.thumbnail_url
                    elif resource.media_type == 2:
                        ext = '.mp4'
                        url = resource.video_url
                    filename = f"{target_username}_latest_post_{i}{ext}"
                    download_file(url, filename)
                    paths.append(filename)
                media = album_upload(client, paths, caption)
                for path in paths:
                    os.remove(path)
            else:
                print("No suitable post found.")
                continue

            # Save the posted media ID to the Firebase Realtime Database
            posted_shortcodes.append(media_shortcode)
            posted_shortcodes_ref.set(posted_shortcodes)

            print(f"Waiting {interval} seconds before the next post...")
            time.sleep(interval)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait a minute before retrying in case of errors

if __name__ == "__main__":
    main()
