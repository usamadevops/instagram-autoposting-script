import os
import time
from instagrapi import Client
from PIL import Image
import requests


def login(username, password):
    print("Logging in...")
    client = Client()
    client.login(username, password)
    print(f"Login successful for user: {username}")
    return client


def fetch_latest_post_image(client, target_username):
    print(f"Fetching the latest post from {target_username}...")
    user_id = client.user_id_from_username(target_username)
    user_media = client.user_medias(user_id, amount=1)
    media = user_media[0]
    media_details = client.media_info(media.pk)

    if media_details.media_type == 1:  # Photo
        image_url = media_details.thumbnail_url
    elif media_details.media_type == 2:  # Video
        print(f"Skipping video post from {target_username}")
        return None
    elif media_details.media_type == 8:  # Carousel
        for item in media_details.carousel:
            if item.media_type == 1:
                image_url = item.thumbnail_url
                break
        else:
            print(f"Skipping carousel post with no image media from {target_username}")
            return None
    else:
        print(f"Unexpected media type from {target_username}")
        return None

    response = requests.get(image_url)
    image_filename = f"{target_username}_latest_post.jpg"

    with open(image_filename, 'wb') as f:
        f.write(response.content)

    print(f"Image fetched: {image_filename}")
    return image_filename




def post_image(client, image_filename):
    print(f"Posting image: {image_filename}")
    caption = f"Posted by {client.username}"
    media = client.photo_upload(image_filename, caption)
    client.media_edit(media.pk, caption)
    print("Image posted.")

def main():
    username = "YOUR_OWN_USERNAME"
    password = "YOUR_ACCOUNT_PASSWORD"
    target_username = "TARGET_USERNAME"
    interval = 60 * 60  # Post every hour

    client = login(username, password)

    while True:
        try:
            image_filename = fetch_latest_post_image(client, target_username)
            post_image(client, image_filename)
            os.remove(image_filename)  # Clean up the downloaded image file
            print(f"Waiting {interval} seconds before the next post...")
            time.sleep(interval)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait a minute before retrying in case of errors


if __name__ == "__main__":
    main()
