import os
import string
import shutil
import re
import time
from instaloader import Instaloader, Post
from instagrapi import Client
from pyrogram import Client as TgClient, filters
from pyrogram.types import Message

L = Instaloader()
client = Client()

api_id = '21179966'
api_hash = 'd97919fb0a3c725e8bb2a25bbb37d57c'
bot_token = '7935736012:AAGG1Xsp3r_-EGpeIN4kzqBZOQZCz_qwARM'

bot = TgClient("insta_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_credentials = {}

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars).strip()

def linkdownload(link):
    id_pattern = r"(/p/|/reel/)([a-zA-Z0-9_-]+)/"
    match = re.search(id_pattern, link)

    if match:
        id = match.group(2)
        post = Post.from_shortcode(L.context, id)
        caption = post.caption if post.caption else "No caption available"
        first_line = caption.split('\n')[0]
        limited_caption = ' '.join(first_line.split()[:6])
        sanitized_caption = sanitize_filename(limited_caption)

        os.makedirs("downloads", exist_ok=True)

        L.download_post(post, target="downloads")

        files = os.listdir("downloads")
        
        video_files = [file for file in files if file.endswith('.mp4')]

        if video_files:
            video_path = os.path.join("downloads", video_files[0])
            new_video_name = f"{sanitized_caption}.mp4"
            new_video_path = os.path.join("downloads", new_video_name)

            os.rename(video_path, new_video_path)
            return new_video_path, sanitized_caption
        else:
            return None, "Error: No video file found in the download folder."
    else:
        return None, "Invalid link! Please provide a valid Instagram post or reel link."

async def upload_video(video_path, caption, username, password, otp=None):
    try:
        if otp:
            client.login(username, password, verification_code=otp)
        else:
            client.login(username, password)
        
        caption1 = f'''♡        🗨️ㅤ     ⎙ㅤ     ⌲  \n{caption} \n .  \n        .     \n      .   \n         . \n
             .        \n         .     \n       .     \n       #bodyart #viralreel #followforfollowback #gymmotivation #reels #instagram #trending #explore 
        #trendingreels #viral #follow #reelfeelkaro #girls #hotgirls #night #umm #tamatar #trend #reels only '''
        
        client.video_upload(video_path, caption1)
    except Exception as e:
        return False, f"Failed to upload the video. Please make sure the video is compatible and try again."

    return True, "Video uploaded successfully."

def clean_downloads_folder():
    folder = "downloads"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def delete_video(video_path):
    if os.path.exists(video_path):
        os.remove(video_path)

@bot.on_message(filters.text)
async def handle_message(client, message: Message):
    user_id = message.from_user.id

    if message.text == "/start":
        await message.reply_text("Welcome! Please use /login to provide your Instagram credentials.")

    elif message.text == "/login":
        if user_id not in user_credentials or user_credentials[user_id].get('step') == 'completed':
            user_data = {'step': 'username'}
            user_credentials[user_id] = user_data
            await message.reply_text("Please provide your Instagram username (format: username).")
        else:
            await message.reply_text("You are already logged in. To update credentials, use /logout.")

    elif user_id in user_credentials and user_credentials[user_id].get('step') == 'completed':
        with open("links.txt", "r") as file:
            links = file.readlines()

        for link in links:
            link = link.strip()
            video_path, result = linkdownload(link)

            if video_path:
                username = user_credentials[user_id]['username']
                password = user_credentials[user_id]['password']
                caption = result
                success, upload_result = await upload_video(video_path, caption, username, password)
                if success:
                    delete_video(video_path)
                    await message.reply_text(f"Video uploaded to Instagram successfully with caption: {caption}. Waiting for the next 6 hours.")
                    time.sleep(6 * 3600)  # 6 hours delay
                else:
                    await message.reply_text(upload_result)
            else:
                await message.reply_text(result)

    else:
        await message.reply_text("Please provide your Instagram username by typing it after /login.")

@bot.on_message(filters.text)
async def handle_login_details(message: Message):
    user_id = message.from_user.id
    user_data = user_credentials.get(user_id, {})

    if user_data.get('step') == 'username':
        username = message.text.strip()
        user_data['username'] = username
        user_data['step'] = 'password'
        await message.reply_text("Please provide your Instagram password.")

    elif user_data.get('step') == 'password':
        password = message.text.strip()
        user_data['password'] = password
        user_data['step'] = 'otp'
        await message.reply_text("Please provide the OTP sent to your Instagram account.")

    elif user_data.get('step') == 'otp':
        otp = message.text.strip()
        user_data['otp'] = otp
        user_data['step'] = 'completed'
        await message.reply_text("Credentials saved! Now you can send an Instagram link to download and upload.")

if __name__ == "__main__":
    print('starting bot...')
    bot.run()
