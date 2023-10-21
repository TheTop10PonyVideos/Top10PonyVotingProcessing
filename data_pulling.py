import csv
import re
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL

API_KEY = 'API TOKEN' # may replace this

youtube = build('youtube', 'v3', developerKey=API_KEY)

def check_privacy_and_get_title(video_id):
    try:
        video_data = youtube.videos().list(
            part='status,snippet',
            id=video_id
        ).execute()

        status = video_data['items'][0]['status']['privacyStatus']
        title = video_data['items'][0]['snippet']['title']
        uploader = video_data['items'][0]['snippet']['channelTitle'] # For Vari Uploader :D
        print(f'Fetched state for {title}. Status: {status}, Uploader: {uploader}')
        return title, status

    except Exception as e:
        return None, f"Error: {str(e)}"
def check_withYtDlp(video_link):
    try:
        with YoutubeDL() as ydl:
            info = ydl.extract_info(video_link, download=False) #This is for vari (uploader getter for blacklist thing for non YT Videos)
            if video_link[:4]:
                info = info['entries'][0]
            title = info['title']
            uploader = info['uploader']
            print(f'Fetched state for {title}. Uploader: {uploader}')
            return title, uploader
    except Exception as e:
        return None, f"Error: {str(e)}"

def extract_video_id(url):
    video_id_match = re.search(r'(?:\?v=|/embed/|/watch\?v=|/youtu.be/)([a-zA-Z0-9_-]+)', url)
    if video_id_match:
        return video_id_match.group(1)
    return None


input_file = 'datalinks.csv'
output_file = 'output_file.csv'

with open(input_file, 'r', encoding='utf-8') as csv_in, open(output_file, 'w', newline='', encoding='utf-8') as csv_out:
    reader = csv.reader(csv_in)
    writer = csv.writer(csv_out)
    
    for row in reader:
        new_row = row  
        
        for index, cell in enumerate(row):
            if 'youtube.com' in cell or 'youtu.be' in cell:
                video_id = extract_video_id(cell)
                
                if video_id:
                    title, privacy_state = check_privacy_and_get_title(video_id)
                    if title is not None:
                        new_row.insert(index + 1, privacy_state)
                    else:
                        new_row.insert(index + 1, 'private')
            else:
                if 'pony.tube' in cell or 'vimeo.com' in cell or 'dailymotion.com' in cell:
                    video_link = cell

                    if video_link:
                        print(video_link)
                        title, status = check_withYtDlp(video_link=video_link)
                        if status is not None:
                            new_row.insert(index + 1, status)
                        else:
                            new_row.insert(index + 1, 'private')
        writer.writerow(new_row)
