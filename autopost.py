import os
import time
from instagrapi import Client
from PIL import Image
import requests
import json
import firebase_admin
from firebase_admin import credentials, db

def login(username, password):
    print("Logging in...")
    client = Client()
    client.login(username, password)
    print(f"Login successful for user: {username}")
    return client

def fetch_latest_post_image(client, target_username, posted_media_ids):
    print(f"Fetching an image post from {target_username}...")
    user_id = client.user_id_from_username(target_username)
    user_media = client.user_medias(user_id, amount=20)

    for media in user_media:
        media_id = media.pk
        if media_id in posted_media_ids:
            continue

        media_details = client.media_info(media.pk)
        caption = media_details.caption_text

        if media_details.media_type == 1:  # Photo
            image_url = media_details.thumbnail_url
        elif media_details.media_type == 8:  # Carousel
            for item in media_details.carousel:
                if item.media_type == 1:
                    image_url = item.thumbnail_url
                    break
            else:
                continue
        else:
            continue

        response = requests.get(image_url)
        image_filename = f"{target_username}_latest_post.jpg"

        with open(image_filename, 'wb') as f:
            f.write(response.content)

        print(f"Image fetched: {image_filename}")
        return image_filename, caption

    print(f"No suitable image post found for {target_username}")
    return None, None, None

def post_image(client, image_filename, caption):
    print(f"Posting image: {image_filename}")
    media = client.photo_upload(image_filename, caption)
    client.media_edit(media.pk, caption)
    print("Image posted.")
    return media.pk

# Load Firebase credentials from the JSON key file
firebase_credentials = credentials.Certificate("service-account-key.json")

# Initialize the Firebase app
firebase_app = firebase_admin.initialize_app(firebase_credentials, {
    'databaseURL': 'https://autopost-9e607-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Get a reference to the posted_media_ids node in the database
posted_media_ids_ref = db.reference('posted_media_ids')

def main():
    username = os.environ["IG_USERNAME"]
    password = os.environ["IG_PASSWORD"]
    target_username = "aiart.ly"
    interval = 60 * 1  # Post every hour


    client = login(username, password)

    # Load posted media IDs from Firebase Realtime Database or create an empty list
    posted_media_ids = posted_media_ids_ref.get() or []

    while True:
        try:
            image_filename, caption = fetch_latest_post_image(client, target_username, posted_media_ids)
            if image_filename and caption:
                posted_media_id = post_image(client, image_filename, caption)
                os.remove(image_filename)  # Clean up the downloaded image file

                # Save the posted media ID to the Firebase Realtime Database
                posted_media_ids.append(posted_media_id)
                posted_media_ids_ref.set(posted_media_ids)

            print(f"Waiting {interval} seconds before the next post...")
            time.sleep(interval)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait a minute before retrying in case of errors

if __name__ == "__main__":
    main()