"""Top 10 Pony Video Squeezer 3000 application."""

import csv, os, shutil, sys
from datetime import datetime
from pathlib import Path
from pytz import timezone
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, filedialog
from modules import init
from functions.voting import (
    load_votes_csv,
    fetch_video_data_for_ballots,
    generate_annotated_csv_data,
)
from functions.date import get_preceding_month_date, is_date_between, get_month_year_bounds, guess_voting_month_year
from functions.video_rules import (
    check_uploader_blacklist,
    check_uploader_whitelist,
    check_upload_date,
    check_duration,
)
from functions.ballot_rules import (
    check_duplicates,
    check_blacklisted_ballots,
    check_non_whitelisted_ballots,
    check_ballot_upload_dates,
    check_ballot_video_durations,
    check_fuzzy,
    check_ballot_uploader_occurrences,
    check_ballot_uploader_diversity,
)
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
    "window": {
        "title": "Top 10 Pony Video Squeezer 3000",
        "width": 800,
        "height": 600,
    },
    "paths": {
        "icon": "images/icon.ico",
        "blacklist": "data/blacklist.txt",
        "whitelist": "data/uploader_whitelist.txt",
        "output": "outputs/processed.csv",
    },
    "fuzzy_similarity_threshold": 80,
    "timezone": timezone("Etc/GMT-14"),
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

    selected_checks = [name for name in check_vars if check_vars[name].get() == True]

    if len(selected_checks) == 0:
        tk.messagebox.showinfo("Error", "Please select at least one check type.")
        return

    inf(f'Preparing to run checks on "{selected_csv_file}"...')

    inf("* Configuring video data fetcher...")
    fetcher = Fetcher()
    fetcher.set_printer(ConsolePrinter())

    # Set up a cache file for video data.
    response_cache_file = os.getenv("response_cache_file")

    if response_cache_file is not None:
        inf(f"  * Fetched video data will be cached in {response_cache_file}.")
        fetcher.set_cache(FileCache(response_cache_file))

    # Configure fetch services. Currently the YouTube Data API and yt-dlp are
    # supported.
    inf("  * Adding fetch services...")
    accepted_domains = []
    with open("modules/csv/accepted_domains.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        accepted_domains = [row[0] for row in reader]

    fetch_services = {
        "YouTube": YouTubeFetchService(API_KEY),
        "yt-dlp": YtDlpFetchService(accepted_domains),
    }

    for name, service in fetch_services.items():
        inf(f'    * Adding "{name}" fetch service.')
        fetcher.add_service(name, service)

    suc(f"  * {len(fetch_services)} fetch services added.")

    # Load all ballots from the CSV file.
    inf(f'Loading all votes from CSV file "{selected_csv_file}"...')
    ballots = load_votes_csv(selected_csv_file)
    total_votes = sum([len(ballot.votes) for ballot in ballots])

    suc(f"Loaded {len(ballots)} ballots containing a total of {total_votes} votes.")

    # Date calculations. There are 3 dates we need to be aware of:
    # Voting date:  The date of the month and year in which the votes were cast.
    #               For example, April 2024. For convenience, we represent this
    #               as a datetime, set to the 1st of the voting month.
    # Upload date:  The date of the month and year in which the videos being
    #               voted on were uploaded. The voting rules require this to be
    #               the month prior to the voting month; ie. if votes were cast
    #               in April 2024, then the votes must be for videos that were
    #               uploaded in March 2024.
    # Current date: The date when the user is running this Python application.
    #               In normal usage, the user will run this in the same month as
    #               the voting month. However, during development, it's common
    #               to use old data for testing. The user will be warned if they
    #               are using old data.

    voting_month, voting_year, is_voting_date_unanimous = guess_voting_month_year(ballots)
    voting_month_date = datetime(voting_year, voting_month, 1)
    voting_month_year_str = voting_month_date.strftime("%B %Y")

    if not is_voting_date_unanimous:
        voting_date_discrepancy_warning = f'Warning: the majority of the ballot timestamps are for {voting_month_year_str}; however, some are for a different month and date. Assuming a voting month of {voting_month_year_str}.'
        err(voting_date_discrepancy_warning)
        tk.messagebox.showinfo("Warning", voting_date_discrepancy_warning)

    upload_month_date = get_preceding_month_date(voting_month_date)
    upload_month_year_str = upload_month_date.strftime("%B %Y")

    current_month_date = datetime.now()
    current_month_year_str = current_month_date.strftime("%B %Y")

    # Give a warning in the console if the CSV is for a different month than the
    # current one.
    anachronistic_ballots = [
        ballot
        for ballot in ballots
        if not is_date_between(ballot.timestamp, *get_month_year_bounds(current_month_date.month, current_month_date.year))
    ]

    if len(anachronistic_ballots) > 0:
        err(
            f"Warning: the input CSV contains votes that do not fall within the current month ({current_month_year_str})."
        )

    inf(f'Date information:')
    inf(f'* Upload month:  {upload_month_year_str}')
    inf(f'* Voting month:  {voting_month_year_str}')
    inf(f'* Current month: {current_month_year_str}')

    # Fetch data for all video URLs that were voted on. The data is indexed by
    # URL to allow lookups when checking the votes. Note that some videos may
    # have no data if their fetch failed; however, they're still included in the
    # results as the votes still reference them.
    inf("Fetching data for all videos...")
    videos = fetch_video_data_for_ballots(ballots, fetcher)

    # Print out a summary of the fetch results (number of successes, failures,
    # etc.)
    suc("Data fetch complete. Result summary:")
    videos_by_label = {}
    for url, video in videos.items():
        label = video.annotations.get_label()
        if label is None:
            label = "successful"
        if label not in videos_by_label:
            videos_by_label[label] = []
        videos_by_label[label].append(video)

    for label, labeled_videos in sorted(videos_by_label.items(), key=lambda i: i[0]):
        suc(f"* {label}: {len(labeled_videos)}")

    # Run some checks to annotate any issues with the videos themselves.
    inf("Performing video checks...")
    videos_with_data = {
        url: video for url, video in videos.items() if video.data is not None
    }

    inf("* Checking for videos from blacklisted uploaders...")
    blacklist_path = Path(CONFIG["paths"]["blacklist"])
    blacklist = [line.strip() for line in blacklist_path.open()]
    check_uploader_blacklist(videos_with_data.values(), blacklist)

    inf("* Checking for videos from whitelisted uploaders...")
    whitelist_path = Path(CONFIG["paths"]["whitelist"])
    whitelist = [line.strip() for line in whitelist_path.open()]
    check_uploader_whitelist(videos_with_data.values(), whitelist)

    inf(f"* Checking video upload dates...")
    check_upload_date(videos_with_data.values(), upload_month_date.month, upload_month_date.year)

    inf(f"* Checking video durations...")
    check_duration(videos_with_data.values())

    suc(f"Video checks complete.")

    # Run checks on the ballots to annotate problematic votes.
    inf("Performing ballot checks...")

    do_check = lambda k: check_vars[k].get() == True

    if do_check("duplicate"):
        inf("* Checking for duplicate votes...")
        check_duplicates(ballots)

    if do_check("blacklist"):
        inf("* Checking for votes for blacklisted videos...")
        check_blacklisted_ballots(ballots, videos)

    if do_check("whitelist"):
        inf("* Checking for votes for non-whitelisted videos...")
        check_non_whitelisted_ballots(ballots, videos)

    if do_check("upload_date"):
        inf("* Checking for votes for videos with invalid upload dates...")
        check_ballot_upload_dates(ballots, videos)

    if do_check("duration"):
        inf("* Checking for votes for videos with invalid durations...")
        check_ballot_video_durations(ballots, videos)

    if do_check("fuzzy"):
        inf("* Performing fuzzy matching checks...")
        check_fuzzy(ballots, videos, CONFIG["fuzzy_similarity_threshold"])

    if do_check("uploader_occurrence"):
        inf("* Checking for ballot uploader occurrences...")
        check_ballot_uploader_occurrences(ballots, videos)

    if do_check("uploader_diversity"):
        inf("* Checking for ballot uploader diversity...")
        check_ballot_uploader_diversity(ballots, videos)

    suc(f"Ballot checks complete.")

    output_csv_path_str = CONFIG["paths"]["output"]
    inf(f"Writing annotated ballot data...")
    output_csv_data = generate_annotated_csv_data(ballots, videos)
    output_csv_path = Path(output_csv_path_str)
    with output_csv_path.open("w", newline="", encoding="utf-8") as output_csv_file:
        output_csv_writer = csv.writer(output_csv_file)
        output_csv_writer.writerows(output_csv_data)

    suc(f'Wrote annotated ballot data to "{output_csv_path_str}".')

    # Write the old-style "shifted cells" CSV. Kept for historical reasons.
    init.add_empty_cells(selected_csv_file, "outputs/shifted_cells.csv")

    suc("Finished checks.")
    tk.messagebox.showinfo("Processing Completed", "Processing Completed")


# TODO: Do we still need this?
def delete_if_present(filepath):
    """Delete the given file if it exists on the filesystem."""
    if os.path.exists(filepath):
        os.remove(filepath)


# Create application window and GUI.
root = tk.Tk()
window_conf = CONFIG["window"]
root.title(window_conf["title"])
root.geometry(f'{window_conf["width"]}x{window_conf["height"]}')

# .ico files unfortunately don't work on Linux due to a known Tkinter issue.
# Current fix is simply to not use the icon on Linux.
if not sys.platform.startswith("linux"):
    root.iconbitmap(CONFIG["paths"]["icon"])

# Create Main Object Frame
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

entry_var = tk.StringVar()
entry = ttk.Entry(main_frame, textvariable=entry_var)
entry.pack(padx=10, pady=10)

browse_button = ttk.Button(
    main_frame, text="📁 Load Votes CSV...", command=browse_file_csv
)
browse_button.pack(pady=10)

checks_frame = tk.LabelFrame(main_frame, text="Checks")
# Create checkboxes and the variables bound to them.
check_labels = {
    "duplicate": "Duplicate Check",
    "blacklist": "Blacklist Check",
    "whitelist": "Whitelist Check",
    "upload_date": "Upload Date Check",
    "duration": "Duration Check",
    "fuzzy": "Fuzzy Check",
    "uploader_occurrence": "Uploader Occurrence Check",
    "uploader_diversity": "Uploader Diversity Check",
}

check_vars = {key: tk.BooleanVar(value=True) for key in check_labels}
check_checkboxes = {
    key: ttk.Checkbutton(checks_frame, text=check_labels[key], variable=check_vars[key])
    for key in check_labels
}

for row, key in enumerate(check_checkboxes):
    checkbox = check_checkboxes[key]
    checkbox.grid(row=row, sticky="W", padx=10)

checks_frame.pack(pady=20)

debug_var = tk.BooleanVar()
debug_checkbox = ttk.Checkbutton(
    main_frame, text="Enable Debug Files (Broken LOL)", variable=debug_var
)
debug_checkbox.pack()

run_button = ttk.Button(main_frame, text="📜 Run Checks", command=run_checks)
run_button.pack(pady=20)

csv_editor = CSVEditor(main_frame)  # Editor main frame
csv_editor.pack()
root.mainloop()
