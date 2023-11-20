import csv
from calculation import data_pulling

titles_file = "modules/csv/datalink.csv"
output_titles = "outputs/titles_output.csv"
output_file = "outputs/processed_titles.csv"

def links_to_titles(input):
    with open(input, "r", encoding="utf-8") as csv_in, open(
        output_titles, "w", newline="", encoding="utf-8"
    ) as csv_out_titles:
        reader = csv.reader(csv_in)
        writer_titles = csv.writer(csv_out_titles)

        for row in reader:
            new_row_titles = row.copy()

            for index, cell in enumerate(row[1:], start=1):
                if "youtube.com" in cell or "youtu.be" in cell:
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, duration, date = data_pulling.ytAPI(video_id)

                        new_row_titles[index] = title
                else:
                    if (
                        "pony.tube" in cell
                        or "vimeo.com" in cell
                        or "dailymotion.com" in cell
                    ):
                        video_link = cell

                        if video_link:
                            title, uploader, duration, date = data_pulling.check_withYtDlp(
                                video_link=video_link
                            )

                            new_row_titles[index] = title

            writer_titles.writerow(new_row_titles)
input_titles_path = "outputs/titles_output.csv"
output_titles_path = 'outputs/calculatedTop10.csv'
def analyze_and_write_titles_to_csv(input_file= input_titles_path, output_file = output_titles_path):
    title_counts = {}
    total_title_count = 0

    with open(input_file, 'r', encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            for title_value in row[1:]:
                if title_value.strip(): 
                    title_counts[title_value] = title_counts.get(title_value, 0) + 1
                    total_title_count += 1

            total_title_count -= 1

    title_percentage = {title: (count / total_title_count) * 100 for title, count in title_counts.items()}

    sorted_titles = sorted(title_percentage.items(), key=lambda x: x[1], reverse=True)

   
    with open(output_file, 'w', newline='', encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Title', 'Percentage'])

        for title, percentage in sorted_titles:
            csvwriter.writerow([title, f'{percentage:.4f}%'])


