"""Top 10 Pony Video Squeezer 3000 application."""
import csv, os, shutil, sys
from datetime import datetime
from pathlib import Path
from pytz import timezone
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, filedialog
from modules import init
from functions.voting import load_votes_csv, fetch_video_data_for_ballots, generate_annotated_csv_data
from functions.date import get_preceding_month_date, is_date_between, get_month_bounds
from functions.video_rules import check_blacklist, check_upload_date, check_duration
from functions.ballot_rules import check_duplicates, check_blacklisted_ballots, check_ballot_upload_dates, check_ballot_video_durations, check_fuzzy, check_ballot_uploader_occurrences, check_ballot_uploader_diversity
from functions.messages import suc, inf, err
from classes.ui import CSVEditor
from classes.fetcher import Fetcher
from classes.fetch_services import YouTubeFetchService, YtDlpFetchService
from classes.caching import FileCache
from classes.printers import ConsolePrinter

# Load environment configuration from a `.env` file if present.
load_dotenv()

API_KEY = os.getenv("apikey")  # may replace this

# Application configuration
CONFIG = {
    'window': {
        'title': "Top 10 Pony Video Squeezer 3000",
        'width': 800,
        'height': 600,
    },
    'paths': {
        'icon': "images/icon.ico",
        'blacklist': "data/blacklist.txt",
        'output': "outputs/processed.csv",
    },
    'fuzzy_similarity_threshold': 80, 
    'timezone': timezone("Etc/GMT-14"),
}

def browse_file_csv():
    """Handler for the "Browse" button. Opens a file dialog and sets the global
    variable `entry_var` to the selected file.
    """
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_var.set(file_path)


def run_checks():
    """Handler for the "Run Checks" button. Reads in the selected CSV file, runs
    a battery of checks on the voting data, and outputs an annotated version of
    the CSV with problematic votes labeled.
    """

    selected_csv_file = entry_var.get()
    if selected_csv_file.strip() == "":
        tk.messagebox.showinfo("Error", "Please select a CSV file first.")
        return
    
    inf(f'Preparing to run checks on "{selected_csv_file}"...')

    inf('* Configuring video data fetcher...')
    fetcher = Fetcher()
    fetcher.set_printer(ConsolePrinter())

    # Set up a cache file for video data.
    response_cache_file = os.getenv("response_cache_file")

    if response_cache_file is not None:
        inf(f'  * Fetched video data will be cached in {response_cache_file}.')
        fetcher.set_cache(FileCache(response_cache_file))

    # Configure fetch services. Currently the YouTube Data API and yt-dlp are
    # supported.
    inf('  * Adding fetch services...')
    accepted_domains = []
    with open("modules/csv/accepted_domains.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        accepted_domains = [
            row[0] for row in reader
        ]

    fetch_services = {
        'YouTube': YouTubeFetchService(API_KEY),
        'yt-dlp': YtDlpFetchService(accepted_domains),
    }

    for name, service in fetch_services.items():
        inf(f'    * Adding "{name}" fetch service.')
        fetcher.add_service(name, service)

    suc(f'  * {len(fetch_services)} fetch services added.')

    # Load all ballots from the CSV file.
    inf(f'Loading all votes from CSV file "{selected_csv_file}"...')
    ballots = load_votes_csv(selected_csv_file)
    total_votes = sum([len(ballot.votes) for ballot in ballots])

    suc(f'Loaded {len(ballots)} ballots containing a total of {total_votes} votes.')

    for ballot in ballots:
        ballot.timestamp = ballot.timestamp.replace(tzinfo=CONFIG['timezone'])

    inf(f'Converting all ballot timestamps to the {CONFIG["timezone"]} timezone.')
    voting_month_date = datetime.now(tz=CONFIG['timezone'])
    upload_month_date = get_preceding_month_date(voting_month_date)
    
    # Give a warning in the console if the CSV is for a different month than the
    # current one.
    anachronistic_ballots = [
        ballot for ballot in ballots
        if not is_date_between(ballot.timestamp, *get_month_bounds(voting_month_date))
    ]
    if len(anachronistic_ballots) > 0:
        voting_month_year_str = voting_month_date.strftime('%B %Y')
        err(f'Warning: the input CSV contains votes that do not fall within the current month ({voting_month_year_str}).')

    # Fetch data for all video URLs that were voted on. The data is indexed by
    # URL to allow lookups when checking the votes. Note that some videos may
    # have no data if their fetch failed; however, they're still included in the
    # results as the votes still reference them.
    inf('Fetching data for all videos...')
    videos = fetch_video_data_for_ballots(ballots, fetcher)

    # Print out a summary of the fetch results (number of successes, failures,
    # etc.)
    suc('Data fetch complete. Result summary:')
    videos_by_label = {}
    for url, video in videos.items():
        label = video.annotations.get_label()
        if label is None:
            label = 'successful'
        if label not in videos_by_label:
            videos_by_label[label] = []
        videos_by_label[label].append(video)

    for label, labeled_videos in sorted(videos_by_label.items(), key=lambda i: i[0]):
        suc(f'* {label}: {len(labeled_videos)}')

    # Run some checks to annotate any issues with the videos themselves.
    inf('Performing video checks...')
    videos_with_data = {url: video for url, video in videos.items() if video.data is not None}

    inf('* Checking for videos from blacklisted uploaders...')
    blacklist_path = Path(CONFIG['paths']['blacklist'])
    blacklist = [line.strip() for line in blacklist_path.open()]
    check_blacklist(videos_with_data.values(), blacklist)

    inf(f'* Checking video upload dates...')
    check_upload_date(videos_with_data.values(), upload_month_date)

    inf(f'* Checking video durations...')
    check_duration(videos_with_data.values())

    suc(f'Video checks complete.')

    # Run checks on the ballots to annotate problematic votes.
    inf('Performing ballot checks...')

    inf('* Checking for duplicate votes...')
    check_duplicates(ballots)
    
    inf('* Checking for votes for blacklisted videos...')
    check_blacklisted_ballots(ballots, videos)

    inf('* Checking for votes for videos with invalid upload dates...')
    check_ballot_upload_dates(ballots, videos)

    inf('* Checking for votes for videos with invalid durations...')
    check_ballot_video_durations(ballots, videos)

    inf('* Performing fuzzy matching checks...')
    check_fuzzy(ballots, videos, CONFIG['fuzzy_similarity_threshold'])

    inf('* Checking for ballot uploader occurrences...')
    check_ballot_uploader_occurrences(ballots, videos)

    inf('* Checking for ballot uploader diversity...')
    check_ballot_uploader_diversity(ballots, videos)

    suc(f'Ballot checks complete.')

    output_csv_path_str = CONFIG['paths']['output']
    inf(f'Writing annotated ballot data...')
    output_csv_data = generate_annotated_csv_data(ballots, videos)
    output_csv_path = Path(output_csv_path_str)
    with output_csv_path.open('w') as output_csv_file:
        output_csv_writer = csv.writer(output_csv_file)
        output_csv_writer.writerows(output_csv_data)

    suc(f'Wrote annotated ballot data to "{output_csv_path_str}".')

    # Write the old-style "shifted cells" CSV. Kept for historical reasons.
    init.add_empty_cells(
        selected_csv_file, "outputs/shifted_cells.csv"
    )

    suc('Finished checks.')
    tk.messagebox.showinfo("Processing Completed", "Processing Completed")


# TODO: Do we still need this?
def delete_if_present(filepath):
    """Delete the given file if it exists on the filesystem."""
    if os.path.exists(filepath):
        os.remove(filepath)


# Create application window and GUI.
root = tk.Tk()
window_conf = CONFIG['window']
root.title(window_conf['title'])
root.geometry(f'{window_conf["width"]}x{window_conf["height"]}')

# .ico files unfortunately don't work on Linux due to a known Tkinter issue.
# Current fix is simply to not use the icon on Linux.
if not sys.platform.startswith("linux"):
    root.iconbitmap(CONFIG['paths']['icon'])

# Create Main Object Frame
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

entry_var = tk.StringVar()
entry = ttk.Entry(main_frame, textvariable=entry_var)
entry.pack(padx=10, pady=10)

browse_button = ttk.Button(main_frame, text="Browse", command=browse_file_csv)
browse_button.pack(pady=10)

# Create checkboxes and the variables bound to them.
check_labels = {
    'debug': 'Enable Debug Files (Broken LOL)',
    'duplicate': 'Duplicate Check',
    'blacklist': 'Blacklist Check',
    'upload_date': 'Upload Date Check',
    'duration': 'Duration Check',
    'fuzzy': 'Fuzzy Check',
    'uploader_occurrence': 'Uploader Occurrence Check',
    'uploader_diversity': 'Uploader Diversity Check',
}

check_vars = {key: tk.BooleanVar(value=True) for key in check_labels}

# Disable the debug checkbox by default.
check_vars['debug'] = tk.BooleanVar()

checkboxes = {
    key: ttk.Checkbutton(main_frame, text=check_labels[key], variable=check_vars[key])
    for key in check_labels
}

for key, checkbox in checkboxes.items():
    if key == 'debug':
        checkbox.pack(pady=40)
    else:
        checkbox.pack()

run_button = ttk.Button(main_frame, text="Run Checks", command=run_checks)
run_button.pack()

csv_editor = CSVEditor(main_frame)  # Editor main frame
csv_editor.pack()
root.mainloop()
