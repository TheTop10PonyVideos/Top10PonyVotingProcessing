"""Top 10 Calculator script. This is typically run by the user after they have
finished running vote-processing.py, as it uses the outputs from that script."""

import csv
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font
from PIL import ImageTk, Image
from functions.top_10_calc import (
    process_shifted_voting_data,
    get_titles_to_urls_mapping,
    get_titles_to_uploaders,
    create_top10_csv_data,
    calc_ranked_records,
    score_by_total_votes,
    score_weight_by_ballot_size,
    load_top_10_master_archive,
    get_history,
)
from functions.date import (
    parse_votes_csv_timestamp,
    get_preceding_month_date,
    get_most_common_month_year,
)
from functions.video_data import fetch_videos_data
from functions.messages import suc, inf, err
from classes.gui import GUI


# A list of year-anniversaries used for the History section (eg. 1 year, 5 year,
# 10 year)
anniversaries = [1, 5, 10]


class Top10Calculator(GUI):
    def __init__(self):
        super().__init__()
        self.rank_algorithms = {
            "total_votes": {
                "label": "Total Votes",
                "tooltip": "Videos are ranked by the total number of votes they received.",
                "var": None,
                "score_func": score_by_total_votes,
                "file_suffix": "",
            },
            "weight_by_ballot_size": {
                "label": "Weight by ballot size",
                "tooltip": "Votes are weighted in proportion to the size of their ballot. This gives more voting power to from people who voted on more videos.",
                "var": None,
                "score_func": score_weight_by_ballot_size,
                "file_suffix": "-weighted-by-ballot-size",
            },
        }

    def gui(self, root):
        root.title("Top 10 Pony Videos: Top 10 Calculator")
        root.geometry(f"860x640")

        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # We're using a single-column grid layout for the main frame. Use
        # columnconfigure to make it stretchable, so that the interface
        # automatically centers when the application is resized.
        main_frame.columnconfigure(0, weight=1)

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(Image.open("images/top-10-calc-ts.png"))
        banner_label = tk.Label(main_frame, image=self.banner_image)
        banner_label.grid(row=0, column=0)

        # Create title
        title_font = Font(size=16)
        title_label = tk.Label(main_frame, font=title_font, text="Top 10 Calculator")
        title_label.grid(row=1, column=0, pady=8)

        # Create a grid to hold the file selectors
        file_selectors_frame = tk.Frame(main_frame)

        # Create "Choose Input CSV..." control
        input_file_label = tk.Label(file_selectors_frame, text="Input CSV file:")

        default_input_file = "outputs/processed.csv"
        self.input_file_var = tk.StringVar()
        self.input_file_var.set(default_input_file)
        input_file_entry = ttk.Entry(
            file_selectors_frame, width=40, textvariable=self.input_file_var
        )

        browse_button = ttk.Button(
            file_selectors_frame,
            text="📁 Choose Input CSV...",
            command=self.browse_input_file,
        )

        input_file_label.grid(column=0, row=0, padx=5, pady=5)
        input_file_entry.grid(column=1, row=0, padx=5, pady=5)
        browse_button.grid(column=2, row=0, padx=5, pady=5, sticky="ew")

        # Create "Choose shifted cells..." control
        shifted_file_label = tk.Label(file_selectors_frame, text="Shifted cells file:")

        default_shifted_file = "outputs/shifted_cells.csv"
        self.shifted_file_var = tk.StringVar()
        self.shifted_file_var.set(default_shifted_file)
        shifted_file_entry = ttk.Entry(
            file_selectors_frame, width=40, textvariable=self.shifted_file_var
        )

        browse_button = ttk.Button(
            file_selectors_frame,
            text="📁 Choose Shifted Cells CSV...",
            command=self.browse_shifted_file,
        )

        shifted_file_label.grid(column=0, row=1, padx=5, pady=5)
        shifted_file_entry.grid(column=1, row=1, padx=5, pady=5)
        browse_button.grid(column=2, row=1, padx=5, pady=5, sticky="ew")

        file_selectors_frame.grid(row=2, column=0)

        # Create Ranking Algorithms frame
        rank_methods_frame = tk.LabelFrame(main_frame, text="Ranking Algorithms")

        # Create variables and checkboxes for ranking methods
        # Auto-select the "Total Votes" ranking algorithm
        for key, algo in self.rank_algorithms.items():
            algo["var"] = tk.BooleanVar(value=True if key == "total_votes" else False)

        # Create checkboxes for ranking methods
        for key, algo in self.rank_algorithms.items():
            algo["checkbox"] = ttk.Checkbutton(
                rank_methods_frame,
                text=algo["label"],
                variable=algo["var"]
            )

        for col, key in enumerate(self.rank_algorithms):
            checkbox = self.rank_algorithms[key]["checkbox"]
            checkbox.grid(row=0, column=col, sticky="N", padx=10, pady=10)

        rank_methods_frame.grid(row=3, column=0, pady=20)

        # Create buttons bar
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0)

        run_button = ttk.Button(
            buttons_frame, text="🧮 Calculate Top 10", command=self.handle_calc
        )
        run_button.grid(column=0, row=0, padx=5, pady=5)

        quit_button = ttk.Button(
            buttons_frame,
            text="Back to Main Menu",
            command=lambda: GUI.run("MainMenu", root),
        )
        quit_button.grid(column=1, row=0, padx=5, pady=5)

    def browse_input_file(self):
        """Handler for the "Choose Input CSV" button. Opens a file dialog and sets the
        global variable `input_file_var` to the selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.input_file_var.set(file_path)

    def browse_shifted_file(self):
        """Handler for the "Choose Shifted Cells CSV" button. Opens a file dialog and sets the
        global variable `input_file_var` to the selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.shifted_file_var.set(file_path)

    def handle_calc(self):
        """Handler for the "Calculate Top 10" button."""
        input_csv_path = self.input_file_var.get()
        urls_csv_path = self.shifted_file_var.get()
        if input_csv_path.strip() == "":
            tk.messagebox.showinfo("Error", "Please select a CSV file.")
            return

        # Get the scoring functions for all ranking methods selected by the
        # user.
        rank_algorithms = [algo for algo in self.rank_algorithms.values() if algo["var"].get()]

        if len(rank_algorithms) == 0:
            tk.messagebox.showinfo("Error", "Please select at least one Ranking Algorithm.")
            return

        inf("Performing Top 10 calculation...")

        shifted_title_rows = None
        shifted_url_rows = None

        try:
            with (
                open(input_csv_path, "r", encoding="utf-8") as titles_csv_file,
                open(urls_csv_path, "r", encoding="utf-8") as urls_csv_file,
            ):
                shifted_titles_reader = csv.reader(titles_csv_file)
                shifted_urls_reader = csv.reader(urls_csv_file)

                shifted_title_rows = [row for row in shifted_titles_reader]
                shifted_url_rows = [row for row in shifted_urls_reader]
        except FileNotFoundError:
            tk.messagebox.showinfo(
                "Error",
                f'Could not find a shifted cells file at "{urls_csv_path}". Maybe you haven\'t run the vote processing script yet?',
            )
            err("Aborted Top 10 calculation due to missing shifted cells file.")
            return

        # Guess the voting month and year from the dates in the timestamps column.
        timestamps = [row[0] for row in shifted_url_rows[1:]]
        timestamp_dates = [
            parse_votes_csv_timestamp(timestamp) for timestamp in timestamps
        ]
        voting_month, voting_year, is_unanimous = get_most_common_month_year(
            timestamp_dates
        )
        voting_date = datetime(voting_year, voting_month, 1)

        # Get the upload date, which is the month prior to the voting date. Remember
        # that votes are always cast for the preceding month's videos - for example,
        # if the voting date is May 2024, then the videos should all be from April
        # 2024. This matters for the history section, as we want the video
        # anniversaries to be relative to when the videos were uploaded.
        upload_date = get_preceding_month_date(voting_date)

        upload_month_year_str = upload_date.strftime("%B %Y")
        inf(
            f"Assuming upload date of {upload_month_year_str} based on most common voting month and year."
        )

        # "Unshift" the titles and URLs CSV data and remove headers/timestamps, so
        # we're left with only the nonempty data cells.
        title_rows = process_shifted_voting_data(shifted_title_rows)
        url_rows = process_shifted_voting_data(shifted_url_rows)

        if len(title_rows) != len(url_rows):
            raise Exception(
                f"Error while processing voting data; number of title and URL rows do not match"
            )

        # Create a dictionary which maps video titles to URLs for each title in the
        # CSV.
        titles_to_urls = get_titles_to_urls_mapping(title_rows, url_rows)

        # Create a dictionary which maps video titles to uploaders for each
        # title in the CSV. This is needed in order to provide the "Uploader"
        # column in the calculated top 10 spreadsheet, which makes it easier to
        # spot uploaders who have somehow managed to get multiple videos into
        # the top 10.
        #
        # Since we only have titles and URLs, we will need to fetch the video
        # data for the given title to determine its uploader.
        youtube_api_key = GUI.yt_api_key_var.get()
        videos_data = fetch_videos_data(youtube_api_key, titles_to_urls.values())
        videos_missing_data = [url for url, data in videos_data.items() if data is None]
        if len(videos_missing_data) > 0:
            err(
                f"WARNING: Could not fetch video data for {len(videos_missing_data)} URLs:"
            )
            for url in videos_missing_data:
                err(f"* {url}")
        titles_to_uploaders = get_titles_to_uploaders(titles_to_urls, videos_data)

        header = ["Title", "Uploader", "Percentage", "Total Votes", "URL", "Notes"]
        # For each ranking method, output a CSV file containing a top 10
        # calculated using it.
        output_csv_paths = []
        master_archive = load_top_10_master_archive()
        for algo in rank_algorithms:
            suc(f'Calculating rankings using "{algo["label"]}" algorithm...')

            output_records = create_top10_csv_data(
                title_rows,
                titles_to_urls,
                titles_to_uploaders,
                algo["score_func"],
                upload_date,
                anniversaries,
                master_archive
            )

            # Write the calculated top 10 to a CSV file.
            output_csv_path_str = f"outputs/calculated_top_10{algo['file_suffix']}.csv"
            output_csv_path = Path(output_csv_path_str)
            output_csv_paths.append(output_csv_path)

            with output_csv_path.open("w", newline="", encoding="utf-8") as output_file:
                output_csv_writer = csv.DictWriter(output_file, fieldnames=header)
                output_csv_writer.writeheader()
                output_csv_writer.writerows(output_records)
                suc(f"* Wrote calculated rankings to {output_csv_path}.")

        suc("Finished.")

        if len(output_csv_paths) == 1:
            tk.messagebox.showinfo(
                "Success",
                f"Top 10 calculation complete. A file containing the video rankings has been created at:\n\n{output_csv_paths[0]}",
            )
        else:
            tk.messagebox.showinfo(
                "Success",
                f"Top 10 calculation complete. {len(output_csv_paths)} files were created: \n\n{'\n'.join([str(p) for p in output_csv_paths])}",
            )

