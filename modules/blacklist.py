import csv
from modules import data_pulling


input_file = 'outputs/processedduplicates.csv'
output_file = 'outputs/processedblacklist.csv'
def checkBlacklist():
    with open(input_file, 'r', encoding='utf-8') as csv_in, open(output_file, 'w', newline='', encoding='utf-8') as csv_out:
        reader = csv.reader(csv_in)
        writer = csv.writer(csv_out)
    
        for row in reader:
            new_row = row
        
            for index, cell in enumerate(row):
                if 'youtube.com' in cell or 'youtu.be' in cell:
                    video_id = data_pulling.extract_video_id(cell)
                
                    if video_id:
                        title, privacy_state, uploader, seconds = data_pulling.check_privacy_and_get_title(video_id)

                        if data_pulling.checkBlacklistedChannels(uploader):
                            new_row[index] = cell + ' [BLACKLISTED]'
                else:
                    if 'pony.tube' in cell or 'vimeo.com' in cell or 'dailymotion.com' in cell:
                        video_link = cell

                        if video_link:
                            print(video_link)
                            title, uploader, seconds = data_pulling.check_withYtDlp(video_link=video_link)
                            if data_pulling.checkBlacklistedChannels(uploader):
                                new_row[index] = cell + ' [BLACKLISTED]'
            writer.writerow(new_row)