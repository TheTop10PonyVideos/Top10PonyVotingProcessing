"""Application for checking the status of videos in the pony archive."""

import tkinter as tk
import googleapiclient.discovery
import csv
import threading
import requests
import math
import io

from googleapiclient.errors import HttpError
from tkinter import filedialog, Event, ttk
from PIL import ImageTk, Image
from typing import List, Tuple
from yt_dlp import YoutubeDL, DownloadError
from enum import Enum
from classes.gui import GUI

class ArchiveIndices:
    LINK = 3
    TITLE = 4
    CHANNEL = 5
    STATE = 7
    ALT_LINK = 8
    FOUND = 9
    NOTES = 10

class States(Enum):
    NON_EMBEDDABLE = ('non-embedable', 'non-embeddable')
    UNAVAILABLE = ('unavailable', 'deleted', 'private', 'tos deleted')
    AGE_RESTRICTED = ('age-restricted',)
    BLOCKED = ('blocked',)

    @classmethod
    def get(cls, value: str):
        for state in cls:
            if value.lower() in state.value:
                return state

blocked_everywhere_indicator = 'EVERYWHERE EXCEPT:'


class ArchiveStatusChecker(GUI):
    def gui(self, root):        
        csv_str: str = requests.get('https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/export?format=csv').content.decode()

        # The requested archive csv comes with extra sets of quotes around titles that include
        # quotation marks so a csv_reader is necessary to accomodate for that
        csv_reader = csv.reader(io.StringIO(csv_str))
        self.archive_rows = [row for row in csv_reader]
        # -1 since the first row is a header
        self.videos_to_fetch = len(self.archive_rows) - 1

        root.title("YouTube Video Status Checker")

        root.geometry("800x600")

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(Image.open("images/archive-checker.png"))
        banner_label = tk.Label(root, image=self.banner_image)
        banner_label.pack()

        youtube_api_key_label = tk.Label(root, text="Enter YouTube Data API Key:")
        youtube_api_key_label.pack()
        self.youtube_api_key_entry = tk.Entry(root, show="*", width=25)
        self.youtube_api_key_entry.pack()

        output_file_frame = tk.Frame(root, pady=10)
        output_file_label = tk.Label(output_file_frame, text="Output CSV file:")

        default_output_file = "outputs/archive_check_results.csv"
        self.output_file_var = tk.StringVar()
        self.output_file_var.set(default_output_file)
        output_file_entry = ttk.Entry(output_file_frame, width=40, textvariable=self.output_file_var)

        browse_button = ttk.Button(
            output_file_frame, text="📁 Choose...", command=self.browse_input_file
        )

        output_file_label.grid(column=0, row=0, padx=5, pady=5)
        output_file_entry.grid(column=1, row=0, padx=5, pady=5)
        browse_button.grid(column=2, row=0, padx=5, pady=5)
        output_file_frame.pack()

        settings_frame = tk.LabelFrame(root, text="Settings")
        settings_frame.pack(pady=5)

        range_frame = tk.Frame(settings_frame)
        range_frame.pack(pady=4)

        range_label = tk.Label(range_frame, text="Range")
        range_label.pack(padx=(5, 5), side="left")

        self.checks_row_start_entry = tk.Entry(range_frame, name="start", width=10)
        self.checks_row_start_entry.bind("<Return>", self.clamp_to_archive_range)
        self.checks_row_start_entry.bind("<FocusOut>", self.clamp_to_archive_range)
        self.checks_row_start_entry.insert(0, 2)
        self.checks_row_start_entry.pack(padx=(5, 5), side="left")

        self.checks_row_end_entry = tk.Entry(range_frame, name="end", width=10)
        self.checks_row_end_entry.bind("<Return>", self.clamp_to_archive_range)
        self.checks_row_end_entry.bind("<FocusOut>", self.clamp_to_archive_range)
        self.checks_row_end_entry.insert(0, len(self.archive_rows))
        self.checks_row_end_entry.pack(padx=(5, 5))

        self.check_titles_var = tk.BooleanVar()
        check_titles = tk.Checkbutton(settings_frame, text="Check Title Differences", variable=self.check_titles_var)
        check_titles.pack(padx=(5, 0), side="left")

        run_frame = tk.Frame(root)
        run_frame.pack(pady=(10, 5))

        start_button = ttk.Button(run_frame, text="Run Status Checker", command=self.run_status_checker)
        start_button.grid(column=0, row=0, padx=5, pady=5)

        quit_button = ttk.Button(run_frame, text="Quit", command=lambda: GUI.run("MainMenu", root))
        quit_button.grid(column=1, row=0, padx=5, pady=5)

        info_frame = tk.Frame(root)
        info_frame.pack()

        self.progress_label = tk.Label(info_frame, text=f"Progress: 0/{self.videos_to_fetch} videos checked")
        self.progress_label.grid(column=0, row=1, padx=3, pady=3)

        self.current_link_label = tk.Label(info_frame, text="Checking: None")
        self.current_link_label.grid(column=0, row=2, padx=3, pady=3)


        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

    def browse_input_file(self):
        """Handler for the "Choose Output CSV" button. Opens a file dialog and sets the
        variable `output_file_var` to the selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.output_file_var.set(file_path)

    def check_non_youtube_video_status(self, video_url) -> Tuple[str, List[States], List[str]]:  
        # Note: During debugging, no videos were found to have any bad status
        # Most of this was copilot generated since it'd be difficult or tedious
        # to check for each platforms edge cases. It's implementation could potentially
        # be inaccurate but in practice should be sufficient enough especially if
        # the debugger is used to manually check and update this code every once in a while

        try:
            states = []

            info_dict = self.ydl.extract_info(video_url, download=False)

            if info_dict.get('upload_date', None):
                visibility = info_dict.get('access_control', {}).get('form', 'Public')
                video_title = info_dict.get("title")
                age_limit = info_dict.get("age_limit")
                availability = info_dict.get("availability")
                geo_restricted = info_dict.get("geo_restricted")
                content_rating = info_dict.get("content_rating")
                status = info_dict.get("status")
                blocked_countries = info_dict.get("blocked_countries", [])
                
                if age_limit and age_limit >= 18:
                    states.append(States.AGE_RESTRICTED)
                
                if geo_restricted or (availability and "blocked" in availability):
                    states.append(States.BLOCKED)
                elif len(blocked_countries) >= 5:
                    states.append(States.BLOCKED)

                if visibility != 'Public':
                    states.append(States.get(visibility))
            else:
                states.append(States.UNAVAILABLE)

            return video_title, states, blocked_countries
        except DownloadError:
            if "vimeo.com" in video_url:
                print(f"\n{video_url} requires a manual check\n")
                return "[COULDN'T FETCH VIMEO DATA]", [], []
            
            return "Video not found", [States.UNAVAILABLE], []

    # Function to check video status using YouTube Data API
    def check_youtube_video_status(self, video_id, tries=0) -> Tuple[str, List[States], List[str]]:
        try:
            response = self.youtube.videos().list(
                part="snippet,contentDetails,status",
                id=video_id
            ).execute()

            if response.get("items"):
                states = []

                item = response["items"][0]
                video_title = item["snippet"]["title"]
                status_info = item.get("status", {})
                video_details = item["contentDetails"]

                if not status_info.get("embeddable"):
                    states.append(States.NON_EMBEDDABLE)
                
                if video_details.get("contentRating", {}).get("ytRating") == "ytAgeRestricted":
                    states.append(States.AGE_RESTRICTED)

                region_restriction = video_details.get("regionRestriction", {})

                blocked_countries = [blocked_everywhere_indicator] + region_restriction.get("allowed") if "allowed" in region_restriction else region_restriction.get("blocked", [])
                if len(blocked_countries) >= 5 or "allowed" in region_restriction:
                    states.append(States.BLOCKED)


                return video_title, states, blocked_countries #status_to_str(privacy_status, blocked_countries, age_restricted), blocked_countries
            else:
                return "Video not found", [States.UNAVAILABLE], []

        except HttpError as e:
            if e.resp.status == 404:
                return "Video not found", [States.UNAVAILABLE], []
            elif e.resp.status == 400 and tries < 3:
                return self.check_youtube_video_status(video_id, self.youtube, tries + 1)
            
            print(f"\033[91m\n{e.reason}")
            quit(1)

    def get_video_status(self, video_url, video_title):
        self.current_link_label.config(text=f"Checking: {video_url}")

        if "youtube.com" in video_url or "youtu.be" in video_url:
            video_id = video_url.split("v=")[-1] if "youtube.com" in video_url else video_url.split("/")[-1]
            updated_video_title, video_states, blocked_countries =  self.check_youtube_video_status(video_id)

        else:
            updated_video_title, video_states, blocked_countries = self.check_non_youtube_video_status(video_url)
            blocked_countries = []


        if updated_video_title == "Video not found":
            updated_video_title = video_title
        
        return updated_video_title, video_states, blocked_countries
                

    # Function to check video status and generate the result CSV
    def run_status_checker(self):
        youtube_api_key = self.youtube_api_key_entry.get().strip()

        if not youtube_api_key: return

        def check_videos():
            ydl_opts = {
                'quiet': True,
                'retries': 3,
                'sleep_interval': 3,
            }

            self.ydl = YoutubeDL(ydl_opts)
            self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=youtube_api_key)


            starting_row_num = int(self.checks_row_start_entry.get())
            processed_videos = 0

            checking_range = self.archive_rows[starting_row_num - 1 : int(self.checks_row_end_entry.get())]
            output_csv_path = self.output_file_var.get()

            if not output_csv_path: return
            
            updated_rows = []
            check_titles = self.check_titles_var.get()
            updated = False

            for i, archive_row in enumerate(checking_range, starting_row_num):
                initial_states = archive_row[ArchiveIndices.STATE].split('/') if len(archive_row[ArchiveIndices.STATE].split('/')) != 1 else archive_row[ArchiveIndices.STATE].split(' & ')
                initial_states = [States.get(state) for state in initial_states if States.get(state) != None]

                video_title = archive_row[ArchiveIndices.TITLE]
                video_url = archive_row[ArchiveIndices.LINK]

                fetched_video_title, video_states, blocked_countries = self.get_video_status(video_url, video_title)
                
                if not fetched_video_title:
                    processed_videos += 1
                    self.progress_label.config(text=f"Progress: {processed_videos}/{self.videos_to_fetch} videos checked")
                    continue

                if (
                    (check_titles and (video_title != fetched_video_title)) or
                    ((len(blocked_countries) >= 5 or blocked_everywhere_indicator in blocked_countries) and States.BLOCKED not in initial_states) or
                    (any(video_state not in initial_states for video_state in video_states)) or
                    (any(archive_state not in video_states for archive_state in initial_states))
                    ):
                    updated_rows.append(["Current", i, video_url, video_title, archive_row[ArchiveIndices.STATE], ''])
                    updated_rows.append(["Updated", i, video_url, fetched_video_title if check_titles else video_title, ' & '.join(map(lambda state: state.value[0], tuple(video_states))) if video_states else '', ', '.join(blocked_countries) if States.BLOCKED in video_states else ''])
                    updated = True
                
                if len(video_states) or len(initial_states):
                    video_url = archive_row[ArchiveIndices.ALT_LINK]
                    _, video_states, blocked_countries = self.get_video_status(video_url, video_title)
                    
                    alt_useable = _ and not (len(video_states) or len(blocked_countries) >= 5 or (len(blocked_countries) < 5 and States.BLOCKED in video_states and blocked_everywhere_indicator not in blocked_countries))

                    if _ and alt_useable and archive_row[ArchiveIndices.FOUND].lower() == 'needed':
                        updated_rows.append(["NOTE", i, video_url, "ALT LINK IS USEABLE BUT LABELED 'needed'", ' & '.join(map(lambda state: state.value[0], tuple(video_states))) if video_states else '', ', '.join(blocked_countries) if States.BLOCKED in video_states else ''])
                        updated = True
                    elif _ and not alt_useable and archive_row[ArchiveIndices.FOUND].lower() != 'needed' and not (States.AGE_RESTRICTED in video_states and 'age restriction' in archive_row[ArchiveIndices.NOTES]):
                        updated_rows.append(["NOTE", i, video_url, "ALT LINK NOT USEABLE", ' & '.join(map(lambda state: state.value[0], tuple(video_states))) if video_states else '', ', '.join(blocked_countries) if States.BLOCKED in video_states else ''])
                        updated = True
                
                if updated:
                    updated_rows.append([""] * 6)
                    updated = False

                processed_videos += 1
                self.progress_label.config(text=f"Progress: {processed_videos}/{self.videos_to_fetch} videos checked")

            # Write to the output CSV with headers
            header = ["", "Archive Row", "Video URL", "Video Title", "Video Status", "Blocked Countries"]
            with open(output_csv_path, 'w', encoding='utf-8') as output_csvfile:
                csv_writer = csv.writer(output_csvfile, lineterminator="\n")
                csv_writer.writerow(header)
                csv_writer.writerows(updated_rows)

            self.result_label.config(text=f"Output CSV saved at: {output_csv_path}")

        # Run the check_videos function in a separate thread
        threading.Thread(target=check_videos).start()

    def clamp_to_archive_range(self, e: Event):
        start = self.checks_row_start_entry.get()
        end = self.checks_row_end_entry.get()

        if e.widget._name == "start":
            end = int(end)

            try:
                start = int(start)
            except:
                self.checks_row_start_entry.delete(0, len(start))
                self.checks_row_start_entry.insert(0, 2)
                self.videos_to_fetch = end - 1
                self.progress_label.config(text=f"Progress: 0/{self.videos_to_fetch} videos checked")
                return

            clamped = max(2, min(start, end))

            if clamped != start:
                self.checks_row_start_entry.delete(
                    0,
                    int(math.log10(abs(start))) + 1 + (abs(start) != start) if start != 0 else 2
                )
                self.checks_row_start_entry.insert(0, clamped)

            self.videos_to_fetch = end - clamped + 1

        elif e.widget._name == "end":
            start = int(start)

            try:
                end = int(end)
            except:
                self.checks_row_end_entry.delete(0, len(end))
                self.checks_row_end_entry.insert(0, len(self.archive_rows))
                self.videos_to_fetch = len(self.archive_rows) - start + 1
                self.progress_label.config(text=f"Progress: 0/{self.videos_to_fetch} videos checked")
                return
            
            clamped = max(start, min(end, len(self.archive_rows)))

            if clamped != end:
                self.checks_row_end_entry.delete(
                    0,
                    int(math.log10(abs(end))) + 1 + (abs(end) != end) if end != 0 else 2
                )
                self.checks_row_end_entry.insert(0, clamped)

            self.videos_to_fetch = clamped - start + 1
        
        self.progress_label.config(text=f"Progress: 0/{self.videos_to_fetch} videos checked")

