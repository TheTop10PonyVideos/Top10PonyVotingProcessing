import csv
from modules import data_pulling

input_file_data_link = 'modules/csv/datalink.csv'
input_file_processed_duplicates = 'outputs/processedduplicates.csv'
output_file = 'outputs/processedblacklist.csv'

def checkBlacklist(input):
    with open(input, 'r', encoding='utf-8') as csv_data_link, \
         open(input_file_processed_duplicates, 'r', encoding='utf-8') as csv_duplicates, \
         open(output_file, 'w', newline='', encoding='utf-8') as csv_out:

        reader_data_link = csv.reader(csv_data_link)
        reader_duplicates = csv.reader(csv_duplicates)
        writer = csv.writer(csv_out)

        for row_data_link, row_duplicates in zip(reader_data_link, reader_duplicates):
            new_row = row_data_link

            for index, cell in enumerate(row_data_link):
                if 'youtube.com' in cell or 'youtu.be' in cell:
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, seconds, date = data_pulling.ytAPI(video_id)

                        if data_pulling.checkBlacklistedChannels(uploader):
                            row_duplicates[index] = cell + ' [BLACKLISTED]'
                else:
                    if 'pony.tube' in cell or 'vimeo.com' in cell or 'dailymotion.com' in cell:
                        video_link = cell

                        if video_link:
                            print(video_link)
                            title, uploader, seconds, date = data_pulling.check_withYtDlp(video_link=video_link)
                            if data_pulling.checkBlacklistedChannels(uploader):
                                row_duplicates[index] = cell + ' [BLACKLISTED]'
            writer.writerow(row_duplicates)


