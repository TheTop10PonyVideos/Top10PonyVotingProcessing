import csv
import requests

youtube_api_key = "EEEEEEEEEEEEEEEEEEEEEE" #may put your api token here

csv_file = 'EEEEEEEEEEEEEE.csv' #may replace this

updated_data = []

with open(csv_file, 'r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
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
        
        api_url = f'https://www.googleapis.com/youtube/v3/videos?key={youtube_api_key}&id={video_id}&part=status'
        response = requests.get(api_url)
        
        if response.status_code == 200:
            video_data = response.json()
            if 'items' in video_data and len(video_data['items']) > 0:
                video_status = video_data['items'][0]['status']['privacyStatus']
                
                row['state'] = video_status
                print(f"Updated state for video: {title} to {video_status}")
            else:
               
                row['state'] = 'Deleted'
                print(f"Video not found in row: {row}! Setting state to 'Deleted'.")
        
       
        updated_data.append(row)

with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    writer.writeheader()
    
    writer.writerows(updated_data)

print("Processing complete. CSV file updated.")
