from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv


api_key = "API KEY LOL" # may replace this lol

csv_file = 'Top_10_Pony_Videos.csv'

youtube = build('youtube', 'v3', developerKey=api_key)

data = []
with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        data.append(row)

for row in data:
    year = row['year']
    month = row['month']
    link = row['link']
    title = row['title']
    channel = row['channel']
    upload_date = row['upload date']
    state = row['state']
    alternate_link = row['alternate link']
    found = row['found']
    notes = row['notes']


    video_id = None
    try:
        video_id = link.split('?v=')[1]
    except IndexError:
        print(f"Invalid YouTube link in row: {row}")
        continue
    
    try:
        response = youtube.videos().list(
            part='status', 
            id=video_id
        ).execute()

        if 'items' in response:
            video_data = response['items'][0]
            video_status = video_data.get('status', {}).get('privacyStatus', '')

            if video_status and video_status != state:
                row['state'] = video_status
                print(f"Updated state for video: {title} to {video_status}")
        else:
            if not state or state.lower() != 'deleted':
                row['state'] = 'Deleted'
                print(f"Video not found. Setting status to 'Deleted' for video: {title}")

    except HttpError as e:
        print(f'An error occurred while fetching video data for row: {row}')
        print(f'Error details: {e}')

with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    fieldnames = data[0].keys()
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    writer.writeheader()
    
    writer.writerows(data)

print("Processing complete. CSV file updated.")
