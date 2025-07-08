"""Top 10 Pony Video Squeezer 3000 (vote processing) application."""

import csv, os, sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font
from PIL import ImageTk, Image
from tktooltip import ToolTip
from functions.general import load_text_data, load_top_10_master_archive
from functions.config import load_config_json
from functions.voting import (
    load_votes_csv,
    normalize_voting_data,
    process_voting_data,
    fetch_video_data_for_ballots,
    generate_annotated_csv_data,
    shift_columns,
)
from functions.date import (
    get_preceding_month_date,
    is_date_between,
    get_month_year_bounds,
    guess_voting_month_year,
)
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
    check_platform,
    check_ballot_uploader_occurrences,
    check_ballot_uploader_diversity,
)
from functions.messages import suc, inf, err
from functions.services import get_fetcher
from functions.similarity import detect_cross_platform_uploads

# from classes.ui import CSVEditor
from classes.gui import GUI


# Application configuration
config = load_config_json("config/config.json")
window_config = {
    "title": "Top 10 Pony Video Squeezer 3000",
    "width": 800,
    "height": 600,
    "banner_image": "images/vote-processing-fs.png",
}


class VoteProcessing(GUI):
    def gui(self, root):
        root.title(window_config["title"])
        root.geometry(f'{window_config["width"]}x{window_config["height"]}')

        # .ico files unfortunately don't work on Linux due to a known Tkinter issue.
        # Current fix is simply to not use the icon on Linux.
        if not sys.platform.startswith("linux"):
            root.iconbitmap(config["paths"]["icon"])

        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(
            Image.open(window_config["banner_image"])
        )
        banner_label = tk.Label(main_frame, image=self.banner_image)

        # Create title
        title_font = Font(size=16)
        title_label = tk.Label(main_frame, font=title_font, text="Vote processing")

        banner_label.pack()
        title_label.pack(pady=16)

        # Create frames for text input control
        inputs_frame = tk.Frame(main_frame, borderwidth=2, relief="ridge")
        csv_input_frame = tk.Frame(inputs_frame)
        inputs_frame.pack()
        csv_input_frame.pack()

        self.csv_entry_var = tk.StringVar()
        input_file_label = tk.Label(csv_input_frame, text="Votes CSV file:")

        input_file_entry = ttk.Entry(csv_input_frame, textvariable=self.csv_entry_var)

        browse_button = ttk.Button(
            csv_input_frame, text="📁 Choose...", command=self.browse_file_csv
        )

        input_file_label.grid(column=0, row=0, padx=8, pady=(2, 8))
        input_file_entry.grid(column=1, row=0, padx=8, pady=(2, 8))
        browse_button.grid(column=2, row=0, padx=8, pady=(2, 8))

        # Create options frame
        options_frame = tk.Frame(main_frame)
        ballot_checks_frame = tk.LabelFrame(options_frame, text="Ballot Checks")
        tools_frame = tk.LabelFrame(options_frame, text="Tools")

        # Create labels and tooltips for options frames
        ballot_check_layout = {
            "uploader_diversity": {
                "label": "Uploader Diversity Check",
                "tooltip": "Annotate ballots that do not contain videos from enough different uploaders.",
            },
            "blacklist": {
                "label": "Blacklist Check",
                "tooltip": "Annotate ballots that contain votes for videos from blacklisted uploaders.",
            },
            "duplicate": {
                "label": "Duplicate Check",
                "tooltip": "Annotate ballots that contain multiple votes for the same video.",
            },
            "upload_date": {
                "label": "Upload Date Check",
                "tooltip": "Annotate ballots that contain votes for videos that do not fall within the voting month.",
            },
            "duration": {
                "label": "Duration Check",
                "tooltip": "Annotate ballots that contain votes for videos that appear to be too short.",
            },
            "uploader_occurrence": {
                "label": "Uploader Occurrence Check",
                "tooltip": "Annotate ballots that contain too many videos from the same uploader.",
            },
            "fuzzy": {
                "label": "Fuzzy Check",
                "tooltip": "Annotate ballots that contain votes with similar titles, uploaders, or durations.",
            },
            "whitelist": {
                "label": "Whitelist Check",
                "tooltip": "Annotate ballots that contain votes for videos from non-whitelisted uploaders.",
            },
            "platform": {
                "label": "Platform Check",
                "tooltip": "Annotate ballots that contain votes for non-youtube videos"
            },
        }

        tools_layout = {
            "detect_cross_platform": {
                "label": "Detect Cross-Platform Uploads",
                "tooltip": "Check for similarities in video titles/uploaders/durations and display a warning in the console if any videos appear to be cross-platform uploads or duplicates.",
            },
            "ensure_complete_data": {
                "label": "Ensure Complete Data",
                "tooltip": "Prompt for manual inputs in the console if a fetched video is missing data.",
            },
            "debug": {
                "label": "Enable Debug Files (Broken LOL)",
            },
        }

        # Create checkboxes for options
        self.ballot_check_vars = {
            key: tk.BooleanVar(value=True) for key in ballot_check_layout
        }
        ballot_check_checkboxes = {
            key: ttk.Checkbutton(
                ballot_checks_frame,
                text=ballot_check_layout[key]["label"],
                variable=self.ballot_check_vars[key],
            )
            for key in ballot_check_layout
        }
        for row, key in enumerate(ballot_check_checkboxes):
            checkbox = ballot_check_checkboxes[key]
            checkbox.grid(row=row, sticky="W", padx=10)

        self.tools_vars = {key: tk.BooleanVar(value=False) for key in tools_layout}
        tools_checkboxes = {
            key: ttk.Checkbutton(
                tools_frame,
                text=tools_layout[key]["label"],
                variable=self.tools_vars[key],
            )
            for key in tools_layout
        }
        for row, key in enumerate(tools_checkboxes):
            checkbox = tools_checkboxes[key]
            checkbox.grid(row=row, sticky="W", padx=10)

        # Auto-set some options
        self.tools_vars["detect_cross_platform"].set(True)

        ballot_checks_frame.grid(row=0, column=0, sticky="N", padx=5, pady=5)
        tools_frame.grid(row=0, column=1, sticky="N", padx=5, pady=5)

        options_frame.pack(pady=10)

        # Add explanatory tooltips
        ttip_delay = 0.5
        ttip_follow = False

        for key in ballot_check_layout:
            if "tooltip" in ballot_check_layout[key]:
                ToolTip(
                    ballot_check_checkboxes[key],
                    msg=ballot_check_layout[key]["tooltip"],
                    delay=ttip_delay,
                    follow=ttip_follow,
                )

        for key in tools_layout:
            if "tooltip" in tools_layout[key]:
                ToolTip(
                    tools_checkboxes[key],
                    msg=tools_layout[key]["tooltip"],
                    delay=ttip_delay,
                    follow=ttip_follow,
                )

        # Create buttons bar
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack()

        run_button = ttk.Button(
            buttons_frame, text="📜 Run Checks", command=self.run_checks
        )
        run_button.grid(column=0, row=0, padx=5, pady=5)

        quit_button = ttk.Button(
            buttons_frame,
            text="Back to Main Menu",
            command=lambda: GUI.run("MainMenu"),
        )
        quit_button.grid(column=1, row=0, padx=5, pady=5)

        # Editor main frame
        # Currently hidden, may be removed in future
        # csv_editor = CSVEditor(main_frame)
        # csv_editor.pack()

    def browse_file_csv(self):
        """Handler for the "Browse" button. Opens a file dialog and sets the global
        variable `entry_var` to the selected file.
        """
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.csv_entry_var.set(file_path)

    def run_checks(self):
        """Handler for the "Run Checks" button. Reads in the selected CSV file, runs
        a battery of checks on the voting data, and outputs an annotated version of
        the CSV with problematic votes labeled.
        """
        youtube_api_key = GUI.get_api_key()
        if not youtube_api_key: return

        selected_csv_file = self.csv_entry_var.get()
        if selected_csv_file.strip() == "":
            tk.messagebox.showinfo("Error", "Please choose a votes CSV file first.")
            return

        selected_checks = [
            name
            for name in self.ballot_check_vars
            if self.ballot_check_vars[name].get() == True
        ]

        if len(selected_checks) == 0:
            tk.messagebox.showinfo("Error", "Please select at least one ballot check.")
            return

        inf(f'Preparing to run checks on "{selected_csv_file}"...')

        fetcher = get_fetcher(
            youtube_api_key, self.tools_vars["ensure_complete_data"].get()
        )

        # Load all ballots from the CSV file.
        inf(f'Loading all votes from CSV file "{selected_csv_file}"...')
        voting_data = load_votes_csv(selected_csv_file)
        inf(f" * Loaded {len(voting_data)} data rows.")

        inf(" * Performing URL normalization...")
        normalized_voting_data = normalize_voting_data(voting_data)

        inf(" * Creating ballots...")
        ballots = process_voting_data(normalized_voting_data)

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

        voting_month, voting_year, is_voting_date_unanimous = guess_voting_month_year(
            ballots
        )
        voting_month_date = datetime(voting_year, voting_month, 1)
        voting_month_year_str = voting_month_date.strftime("%B %Y")

        if not is_voting_date_unanimous:
            inf(
                f"Note: the majority of the ballot timestamps are for {voting_month_year_str}; however, some are for a different month and date. Assuming a voting month of {voting_month_year_str}."
            )

        upload_month_date = get_preceding_month_date(voting_month_date)
        upload_month_year_str = upload_month_date.strftime("%B %Y")

        current_month_date = datetime.now()
        current_month_year_str = current_month_date.strftime("%B %Y")

        # Give a warning in the console if the CSV is for a different month than the
        # current one.
        anachronistic_ballots = [
            ballot
            for ballot in ballots
            if not is_date_between(
                ballot.timestamp,
                *get_month_year_bounds(
                    current_month_date.month, current_month_date.year
                ),
            )
        ]

        if len(anachronistic_ballots) > 0:
            err(
                f"Warning: the input CSV contains votes that do not fall within the current month ({current_month_year_str})."
            )

        inf(f"Date information:")
        inf(f"* Upload month:  {upload_month_year_str}")
        inf(f"* Voting month:  {voting_month_year_str}")
        inf(f"* Current month: {current_month_year_str}")

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

        for label, labeled_videos in sorted(
            videos_by_label.items(), key=lambda i: i[0]
        ):
            suc(f"* {label}: {len(labeled_videos)}")

        # Perform a check for cross-platform uploads.
        found_possible_cross_platform = False
        if self.tools_vars["detect_cross_platform"].get():
            inf("Attempting to detect cross-platform or duplicate uploads...")
            similarity_table = detect_cross_platform_uploads(videos)

            if len(similarity_table) > 0:
                found_possible_cross_platform = True
                err(
                    f"Warning: {len(similarity_table)} videos look like they may be cross-platform uploads or duplicates:"
                )
                for url, subtable in similarity_table.items():
                    title = None
                    if url in videos:
                        video = videos[url]
                        title = video.data["title"]
                    if title is None:
                        err(f"* {url}:")
                    else:
                        err(f"* {title} ({url}):")

                    for similarity_url, similarity_props in subtable.items():
                        similarity_props_str = ", ".join(similarity_props)
                        err(f"  * Similar {similarity_props_str} to {similarity_url}")
            else:
                inf("No cross-platform or duplicate uploads were detected.")

        # Run some checks to annotate any issues with the videos themselves.
        inf("Performing video checks...")
        videos_with_data = {
            url: video for url, video in videos.items() if video.data is not None
        }

        inf(f"* Checking video upload dates...")
        check_upload_date(
            videos_with_data.values(), upload_month_date.month, upload_month_date.year
        )

        inf(f"* Checking video durations...")
        check_duration(videos_with_data.values())

        inf("* Checking for videos from blacklisted uploaders...")
        uploader_blacklist = load_text_data(config["paths"]["uploader_blacklist"])
        check_uploader_blacklist(videos_with_data.values(), uploader_blacklist)

        inf("* Checking for videos from whitelisted uploaders...")
        uploader_whitelist = set(row["channel"].removeprefix("[BLACKLIST] ") for row in load_top_10_master_archive(False))
        check_uploader_whitelist(videos_with_data.values(), uploader_whitelist)

        suc(f"Video checks complete.")

        # Run checks on the ballots to annotate problematic votes. These checks
        # should be ordered most important first, to make the more important
        # annotations appear first in the CSV.
        inf("Performing ballot checks...")

        do_check = lambda k: self.ballot_check_vars[k].get() == True

        if do_check("uploader_diversity"):
            inf("* Checking for ballot uploader diversity...")
            check_ballot_uploader_diversity(ballots, videos)

        if do_check("blacklist"):
            inf("* Checking for votes for blacklisted videos...")
            check_blacklisted_ballots(ballots, videos)

        if do_check("duplicate"):
            inf("* Checking for duplicate votes...")
            check_duplicates(ballots)

        if do_check("upload_date"):
            inf("* Checking for votes for videos with invalid upload dates...")
            check_ballot_upload_dates(ballots, videos)

        if do_check("duration"):
            inf("* Checking for votes for videos with invalid durations...")
            check_ballot_video_durations(ballots, videos)

        if do_check("uploader_occurrence"):
            inf("* Checking for ballot uploader occurrences...")
            check_ballot_uploader_occurrences(ballots, videos)

        if do_check("fuzzy"):
            inf("* Performing fuzzy matching checks...")
            fuzzy_similarity_threshold = 80
            check_fuzzy(ballots, videos, fuzzy_similarity_threshold)

        if do_check("whitelist"):
            inf("* Checking for votes for non-whitelisted videos...")
            check_non_whitelisted_ballots(ballots, videos)

        if do_check("platform"):
            inf("* Checking for votes for non-YouTube videos")
            check_platform(ballots, videos)

        suc(f"Ballot checks complete.")

        output_csv_path_str = config["paths"]["output"]
        inf(f"Writing annotated ballot data...")
        output_csv_data = generate_annotated_csv_data(ballots, videos)
        output_csv_path = Path(output_csv_path_str)
        with output_csv_path.open("w", newline="", encoding="utf-8") as output_csv_file:
            output_csv_writer = csv.writer(output_csv_file)
            output_csv_writer.writerows(output_csv_data)

        suc(f'Wrote annotated ballot data to "{output_csv_path_str}".')

        # Write the voting data to the "shifted cells" CSV. This is needed in order
        # to ensure that we can match the cells in the annotated voting CSV (which
        # contains only video titles) to the URLs that correspond to those titles.
        shifted_cells_path = Path(config["paths"]["shifted_cells"])

        inf(f'Writing "shifted cells" CSV...')
        shifted_voting_data = shift_columns(normalized_voting_data)

        with (
            shifted_cells_path.open(
                "w", newline="", encoding="utf-8"
            ) as shifted_cells_file,
        ):
            writer = csv.writer(shifted_cells_file)
            writer.writerows(shifted_voting_data)

        suc(f'Wrote "shifted cells" data to "{shifted_cells_path}".')

        suc("Finished checks.")

        proc_complete_msgs = []
        proc_complete_msgs.append(
            f"Vote processing complete. An annotated ballot data file has been created at:\n\n{output_csv_path_str}"
        )
        if found_possible_cross_platform:
            proc_complete_msgs.append(
                "Detected some possible cross-platform uploads. See the console output for more details."
            )

        proc_complete_msg = "\n\n".join(proc_complete_msgs)

        tk.messagebox.showinfo("Processing Completed", proc_complete_msg)

    # TODO: Do we still need this?
    def delete_if_present(self, filepath):
        """Delete the given file if it exists on the filesystem."""
        if os.path.exists(filepath):
            os.remove(filepath)
