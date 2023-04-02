# Instagram Repost Bot

This Instagram Repost Bot allows you to automatically repost the latest media (images, videos, reels, IGTV, and albums) from a target Instagram user to your own Instagram account. It periodically checks for new posts and uploads them to your account with the original caption.

## Features

- Supports various media types (images, videos, reels, IGTV, and albums)
- Automatically reposts the latest media from a target Instagram account
- Preserves the original caption
- Prevents reposting the same media
- Uses Firebase Realtime Database to store posted media shortcodes

## Dependencies

- [instagrapi](https://pypi.org/project/instagrapi/)
- [Pillow](https://pypi.org/project/Pillow/)
- [requests](https://pypi.org/project/requests/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [firebase-admin](https://pypi.org/project/firebase-admin/)

## Setup

1. Install the required dependencies:

```
pip install instagrapi Pillow requests python-dotenv firebase-admin
```

2. Create a `.env` file in the project directory with the following variables:

```
IG_USERNAME=<your_instagram_username>
IG_PASSWORD=<your_instagram_password>
TARGET_USERNAME=<target_instagram_username>
DATABASE_URL=<your_firebase_database_url>
```

Replace `<your_instagram_username>`, `<your_instagram_password>`, `<target_instagram_username>`, and `<your_firebase_database_url>` with your Instagram account credentials, the target Instagram account username, and your Firebase Realtime Database URL, respectively.

3. Download your Firebase Service Account Key JSON file from the Firebase Console and save it as `service-account-key.json` in the project directory.

4. Run the script:

```
python repost_bot.py
```

The bot will now periodically check for new posts from the target Instagram account and repost them to your account. It will also store the shortcodes of the posted media in the Firebase Realtime Database to prevent reposting the same media again.

## Customization

- You can change the interval between repost attempts by modifying the `interval` variable in the `main` function. The default value is set to 60 seconds.

```python
interval = 60  # Set the interval between repost attempts (in seconds)

##Disclaimer

This script is for educational purposes only. Please respect Instagram's terms of service and use responsibly.




