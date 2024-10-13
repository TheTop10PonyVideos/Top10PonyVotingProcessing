"""Application for checking the status of videos in the pony archive."""

import tkinter as tk
import csv
import threading
import requests
import io
import asyncio
import aiohttp
import json
import os

from tkinter import filedialog, Event, ttk
from PIL import ImageTk, Image
from typing import List, Tuple
from yt_dlp import YoutubeDL, DownloadError
from enum import Enum
from classes.gui import GUI


blocked_everywhere_indicator = 'EVERYWHERE EXCEPT:'
video_not_found = "Video not found"
lock = asyncio.Lock()
archive_url = 'https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/export?format=csv'


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


class ArchiveStatusChecker(GUI):
    def __init__(self):
        super().__init__()
        self.running = False
        self.output_csv_path = ""
        self.checking_range = []
        self.processed_videos = 0
        self.starting_row_num = 2
        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)

    def gui(self, root):

        # Only get archive or check for updates when it's not being checked so full progress
        # label and output path is displayed upon revisiting
        if not self.running:     
            csv_str: str = requests.get(archive_url).content.decode()

            # The requested archive csv comes with extra sets of quotes around titles that include
            # quotation marks so a csv_reader is necessary to accomodate for that
            csv_reader = csv.reader(io.StringIO(csv_str))
            self.archive_rows = [row for row in csv_reader]
            # -1 since the first row is a header
            self.videos_to_fetch = len(self.archive_rows) - 1

        root.title("YouTube Video Status Checker")

        root.geometry("800x600")
        root.grid_columnconfigure(0, weight=1)

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(Image.open("images/archive-checker.png"))
        banner_label = tk.Label(root, image=self.banner_image)
        banner_label.grid(column=0, row=0)

        youtube_api_key_label = tk.Label(root, text="Enter YouTube Data API Key:")
        youtube_api_key_label.grid(column=0, row=1)

        self.youtube_api_key_entry = tk.Entry(root, show="*", width=30)
        self.youtube_api_key_entry.grid(column=0, row=2, pady=5)

        self.input_file_var = tk.StringVar()
        self.input_file_frame = tk.Frame(root)
        self.input_file_frame.grid(column=0, row=3)

        output_file_frame = tk.Frame(root, pady=5)
        output_file_label = tk.Label(output_file_frame, text="Output CSV file:")

        self.default_output_file = "outputs/archive_check_results"

        if os.path.exists(f"{self.default_output_file}.csv"):
            i = 2

            while os.path.exists(f"{self.default_output_file}{i}.csv"):
                i += 1

            self.default_output_file = f"{self.default_output_file}{i}"
        
        self.default_output_file += ".csv"

        self.output_file_var = tk.StringVar(value=self.default_output_file)
        output_file_entry = tk.Entry(output_file_frame, width=40, textvariable=self.output_file_var)

        browse_button = ttk.Button(
            output_file_frame, text="📁 Choose...", command=self.browse_output_file
        )

        output_file_label.grid(column=0, row=0, padx=5)
        output_file_entry.grid(column=1, row=0, padx=5)
        browse_button.grid(column=2, row=0, padx=5)
        output_file_frame.grid(column=0, row=4)

        settings_frame = tk.LabelFrame(root, text="Settings")
        settings_frame.grid(column=0, row=5, pady=5)

        range_frame = tk.Frame(settings_frame)
        range_frame.grid(column=0, row=0, pady=4)

        range_label = tk.Label(range_frame, text="Range")
        range_label.pack(padx=(5, 5), side="left")

        self.checks_row_start_entry = tk.Entry(range_frame, name="start", width=10)
        self.checks_row_start_entry.bind("<Return>", self.clamp_to_archive_range)
        self.checks_row_start_entry.bind("<FocusOut>", self.clamp_to_archive_range)
        self.checks_row_start_entry.insert(0, self.starting_row_num if self.running else 2)
        self.checks_row_start_entry.config(state=tk.DISABLED if self.running else tk.NORMAL)
        self.checks_row_start_entry.pack(padx=(5, 5), side="left")

        self.checks_row_end_entry = tk.Entry(range_frame, name="end", width=10)
        self.checks_row_end_entry.bind("<Return>", self.clamp_to_archive_range)
        self.checks_row_end_entry.bind("<FocusOut>", self.clamp_to_archive_range)
        self.checks_row_end_entry.insert(0, self.starting_row_num + len(self.checking_range) - 1 if self.running else len(self.archive_rows))
        self.checks_row_end_entry.config(state=tk.DISABLED if self.running else tk.NORMAL)
        self.checks_row_end_entry.pack(padx=(5, 5))

        self.check_titles_var = tk.BooleanVar()
        check_titles = tk.Checkbutton(settings_frame, text="Check Title Differences", variable=self.check_titles_var)
        check_titles.grid(column=0, row=1, padx=(5, 0), sticky="w")

        self.use_async_var = tk.BooleanVar(value=True)
        # Still be kept optional in case something goes wrong in which case synchronous fetching can stil be used
        use_async = tk.Checkbutton(settings_frame, text="Async Requests (faster)", variable=self.use_async_var)
        use_async.grid(column=0, row=2, padx=(5, 0), sticky="w")

        self.contrast_states_var = tk.BooleanVar(value=False)
        contrast_states = tk.Checkbutton(settings_frame, text="Contrast States", variable=self.contrast_states_var)
        contrast_states.grid(column=0, row=3, padx=(5, 0), sticky="w")

        self.generic_list_var = tk.BooleanVar(value=False)
        generic_list = tk.Checkbutton(settings_frame, text="Generic List", variable=self.generic_list_var, command=self.generic_list_checked)
        generic_list.grid(column=0, row=4, padx=(5, 0), sticky="w")

        run_frame = tk.Frame(root)
        run_frame.grid(column=0, row=6, pady=(10, 5))

        self.start_button = ttk.Button(run_frame, text="Run Status Checker", command=self.run_status_checker, state=tk.DISABLED if self.running else tk.NORMAL)
        self.start_button.grid(column=0, row=0, padx=5, pady=5)

        quit_button = ttk.Button(run_frame, text="Quit", command=lambda: GUI.run("MainMenu", root))
        quit_button.grid(column=1, row=0, padx=5, pady=5)

        info_frame = tk.Frame(root)
        info_frame.grid(column=0, row=7)

        self.progress_label = tk.Label(info_frame, text=f"Progress: {self.processed_videos if self.running else 0}/{self.videos_to_fetch} videos checked")
        self.progress_label.grid(column=0, row=1, padx=3, pady=3)

        self.result_label = tk.Label(root, text=self.output_csv_path if len(self.checking_range) and (self.processed_videos == len(self.checking_range)) else "")
        self.result_label.grid(column=0, row=8, pady=10)

    def generic_list_checked(self):
        """Called whenever the check box for a generic list is pressed.
        Changes the ui to allow status checking a csv file instead of the archive"""
        checked = self.generic_list_var.get()

        if not checked:
            for child in self.input_file_frame.winfo_children():
                child.destroy() # RIP childs again
            
            self.input_file_var.set("")
            self.videos_to_fetch = len(self.archive_rows) - 1

            self.checks_row_start_entry.config(state=tk.NORMAL)
            self.checks_row_start_entry.delete(0, tk.END)
            self.checks_row_start_entry.insert(0, 2)
            self.checks_row_end_entry.config(state=tk.NORMAL)
            self.checks_row_end_entry.delete(0, tk.END)
            self.checks_row_end_entry.insert(0, len(self.archive_rows))
            self.progress_label.config(text=f"Progress: 0/{self.videos_to_fetch} videos checked")
            self.start_button.config(state=tk.NORMAL)

            return self.input_file_frame.grid_remove()

        tk.Label(self.input_file_frame, text="Input CSV File:").grid(column=0, row=0, padx=5)
        tk.Entry(self.input_file_frame, width=40, textvariable=self.input_file_var, state="readonly").grid(column=1, row=0, padx=5)
        ttk.Button(self.input_file_frame, text="📁 Choose...", command=self.browse_input_file).grid(column=2, row=0, padx=5)
        self.input_file_frame.grid()

        self.checks_row_start_entry.delete(0, tk.END)
        self.checks_row_start_entry.config(state="readonly")
        self.checks_row_end_entry.delete(0, tk.END)
        self.checks_row_end_entry.config(state="readonly")
        self.start_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Progress: -/- videos checked")

    def browse_output_file(self):
        """Handler for the "Choose Output CSV" button. Opens a file dialog and sets the
        variable `output_file_var` to the selected file."""
        file_path = filedialog.asksaveasfilename(filetypes=[("CSV Files", "*.csv")])
        
        if file_path and not file_path.endswith(".csv"):
            file_path += ".csv"

        self.output_file_var.set(file_path if file_path else self.default_output_file)

    def browse_input_file(self):
        """Handler for the "Choose Input CSV" button. Opens a file dialog and sets the
        variable `input_file_var` to the selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        self.input_file_var.set(file_path)

        if not file_path:
            self.checks_row_start_entry.delete(0, tk.END)
            self.checks_row_start_entry.config(state="readonly")
            self.checks_row_end_entry.delete(0, tk.END)
            self.checks_row_end_entry.config(state="readonly")
            self.start_button.config(state=tk.DISABLED)
            self.progress_label.config(text="Progress: -/- videos checked")
            return
        
        with open(file_path, "r", encoding="utf-8") as input_csv_file:
            csv_reader = csv.reader(input_csv_file)
            self.checking_range = [row for row in csv_reader]
            self.videos_to_fetch = len(self.checking_range)

            self.checks_row_start_entry.config(state=tk.NORMAL)
            self.checks_row_start_entry.delete(0, tk.END)
            self.checks_row_start_entry.insert(0, 1)
            self.checks_row_end_entry.config(state=tk.NORMAL)
            self.checks_row_end_entry.delete(0, tk.END)
            self.checks_row_end_entry.insert(0, len(self.checking_range))
            self.progress_label.config(text=f"Progress: 0/{self.videos_to_fetch} videos checked")
            self.start_button.config(state=tk.NORMAL)

    def check_non_youtube_video_status(self, video_url) -> Tuple[str, List[States], List[str]]:
        """Get the current state of a video using the yt-dlp module""" 
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

                # if status or content_rating:
                #    print(status, content_rating)

                blocked_countries = info_dict.get("blocked_countries", [])
                
                if age_limit and age_limit >= 18:
                    states.append(States.AGE_RESTRICTED)
                
                if geo_restricted or (availability and "blocked" in availability) or len(blocked_countries) >= 5:
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
            
            return video_not_found, [States.UNAVAILABLE], []

    async def check_youtube_video_status(self, video_id, tries=0) -> Tuple[str, List[States], List[str]]:
        """Get the current state of a video using the Youtube Data API"""
        try:
            async with self.session.get(
                f"https://www.googleapis.com/youtube/v3/videos?key={self.youtube_api_key}&id={video_id}&part=snippet,contentDetails,status"
            ) as response:
                response = json.loads(await response.text())

                if response.get("items"):
                    states = [];

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


                    return video_title, states, blocked_countries
                else:
                    return video_not_found, [States.UNAVAILABLE], []

        except Exception as e:
            if e.resp.status == 404:
                return video_not_found, [States.UNAVAILABLE], []
            elif e.resp.status == 400 and tries < 3:
                return self.check_youtube_video_status(video_id, tries + 1)
            
            print(f"\033[91m\n{e.reason}")
            quit(1)

    async def get_video_status(self, video_url, video_title):
        """Get the current state of the video from the given any supported link"""
        if "youtube.com" in video_url or "youtu.be" in video_url:
            video_id = video_url.split("v=")[-1] if "youtube.com" in video_url else video_url.split("/")[-1]
            updated_video_title, video_states, blocked_countries = await self.check_youtube_video_status(video_id)

        else:
            updated_video_title, video_states, blocked_countries = self.check_non_youtube_video_status(video_url)
            blocked_countries = []


        if updated_video_title == video_not_found:
            updated_video_title = video_title
        
        return updated_video_title, video_states, blocked_countries
    
    def write_to_output_csv(self):
        """Writes the discrepancies from the list of notes into a csv file"""
        header = ["", "Archive Row", "Video URL", "Video Title", "Video Status", "Blocked Countries"]
        with open(self.output_csv_path, 'w', encoding='utf-8') as output_csvfile:
            csv_writer = csv.writer(output_csvfile, lineterminator="\n")
            
            if not self.generic_list_var.get():
                csv_writer.writerow(header)
            
            csv_writer.writerows(self.updated_rows)

        if self == GUI.active_gui and self.ready:
            self.result_label.config(text=f"Output CSV saved at: {self.output_csv_path}")
    
    # Increment the progress counter and signal when the checking process is done
    async def update_progress(self):
        """Increment the displayed progress label, and close the aiohttp session
        when all videos have been processed"""
        self.processed_videos += 1
        if self == GUI.active_gui and self.ready:
            self.progress_label.config(text=f"Progress: {self.processed_videos}/{self.videos_to_fetch} videos checked")

        if self.processed_videos == len(self.checking_range):
            self.write_to_output_csv()
            self.running = False

            if self == GUI.active_gui and self.ready:
                self.start_button.config(state=tk.NORMAL)
                self.checks_row_start_entry.config(state=tk.NORMAL)
                self.checks_row_end_entry.config(state=tk.NORMAL)

            await self.session.close()


    # The starting point for the main part of this process
    def run_status_checker(self):
        """Check the status of the archive or generic list and output a csv
        file of discrepancies or bad links respectively"""
        self.youtube_api_key = self.youtube_api_key_entry.get().strip()
        if not self.youtube_api_key: return
        
        output_file_dir = self.output_file_var.get()
        if not output_file_dir: return
        
        self.output_csv_path = output_file_dir

        ydl_opts = {
            'quiet': True,
            'retries': 3,
            'sleep_interval': 3,
            "allowed_extractors": ["twitter", "Newgrounds", "lbry", "TikTok", "PeerTube", "vimeo", "BiliBili", "dailymotion", "generic"]
        }

        self.ydl = YoutubeDL(ydl_opts)        
        generic = self.generic_list_var.get()

        self.starting_row_num = int(self.checks_row_start_entry.get())

        if generic:
            self.checking_range = self.checking_range[self.starting_row_num - 1 : int(self.checks_row_end_entry.get())]
        else:
            self.checking_range = self.archive_rows[self.starting_row_num - 1 : int(self.checks_row_end_entry.get())]

        self.updated_rows = []
        self.processed_videos = 0
        self.check_titles = self.check_titles_var.get()
        
        # Run the check_videos function in a separate thread
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.checks_row_start_entry.config(state=tk.DISABLED)
        self.checks_row_end_entry.config(state=tk.DISABLED)

        if generic:
            if self.use_async_var.get():
                threading.Thread(target=lambda: self.async_loop.run_until_complete(self.check_generic_async())).start()
            else:
                threading.Thread(target=lambda: asyncio.run(self.check_generic_sync())).start()
        else:
            if self.use_async_var.get():
                threading.Thread(target=lambda: self.async_loop.run_until_complete(self.check_videos_async())).start()
            else:
                threading.Thread(target=lambda: asyncio.run(self.check_videos_sync())).start()

    async def check_video(self, row_index: int, archive_row: List[str]):
        """Compare the current state of a video with its corresponding archive entry, and note
        differences in states. Also checks the alt link when appropriate"""
        initial_states = archive_row[ArchiveIndices.STATE].split('/') if len(archive_row[ArchiveIndices.STATE].split('/')) != 1 else archive_row[ArchiveIndices.STATE].split(' & ')
        initial_states = [States.get(state) for state in initial_states if States.get(state) != None]

        video_title = archive_row[ArchiveIndices.TITLE]
        video_url = archive_row[ArchiveIndices.LINK]

        fetched_video_title, video_states, blocked_countries = await self.get_video_status(video_url, video_title)

        updated = False

        # This lock makes sure that line breaks and related items appended to updated_rows stay consistent
        async with lock:
            needs_updating = (
                (self.check_titles and (video_title != fetched_video_title)) or
                ((len(blocked_countries) >= 5 or blocked_everywhere_indicator in blocked_countries) and States.BLOCKED not in initial_states) or
                (any(video_state not in initial_states for video_state in video_states)) or
                (any(archive_state not in video_states for archive_state in initial_states))
            ) if self.contrast_states_var.get() else (
                (self.check_titles and (video_title != fetched_video_title)) or
                (bool(len(video_states)) != bool(len(initial_states)))
            )

            if needs_updating:
                self.updated_rows.append(["Current", row_index, video_url, video_title, archive_row[ArchiveIndices.STATE], ''])
                self.updated_rows.append(["Updated", row_index, video_url, fetched_video_title if self.check_titles else video_title, ' & '.join(map(lambda state: state.value[0], tuple(video_states))) if video_states else '', ', '.join(blocked_countries) if States.BLOCKED in video_states else ''])
                updated = True
            
            if len(video_states) or len(initial_states):
                video_url = archive_row[ArchiveIndices.ALT_LINK]
                _, video_states, blocked_countries = await self.get_video_status(video_url, video_title)
                
                alt_useable = _ and not (len(video_states) or len(blocked_countries) >= 5 or (len(blocked_countries) < 5 and States.BLOCKED in video_states and blocked_everywhere_indicator not in blocked_countries))

                if _ and alt_useable and archive_row[ArchiveIndices.FOUND].lower() == 'needed':
                    self.updated_rows.append(["NOTE", row_index, video_url, "ALT LINK IS USEABLE BUT LABELED 'needed'", ' & '.join(map(lambda state: state.value[0], tuple(video_states))) if video_states else '', ', '.join(blocked_countries) if States.BLOCKED in video_states else ''])
                    updated = True
                elif _ and not alt_useable and archive_row[ArchiveIndices.FOUND].lower() != 'needed' and not (States.AGE_RESTRICTED in video_states and 'age restriction' in archive_row[ArchiveIndices.NOTES]):
                    self.updated_rows.append(["NOTE", row_index, video_url, "ALT LINK NOT USEABLE", ' & '.join(map(lambda state: state.value[0], tuple(video_states))) if video_states else '', ', '.join(blocked_countries) if States.BLOCKED in video_states else ''])
                    updated = True
            
            if updated:
                self.updated_rows.append([""] * 6)

            await self.update_progress()

    async def check_link(self, row_index, video_url):
        """Check the video status of a video link, and create a note if it has a bad state"""
        fetched_video_title, video_states, blocked_countries = await self.get_video_status(video_url, "")
                
        if len(blocked_countries) >= 5 or blocked_everywhere_indicator in blocked_countries:
            video_states.append(States.BLOCKED)

        # This lock makes sure that line breaks and related items appended to updated_rows stay consistent
        async with lock:
            if len(video_states):
                self.updated_rows.append(["Bad Status", row_index, video_url, fetched_video_title , ' & '.join(map(lambda state: state.value[0], tuple(video_states))), ', '.join(blocked_countries) if States.BLOCKED in video_states else ''])
                self.updated_rows.append([""] * 6)

            await self.update_progress()

    async def check_videos_async(self):
        self.session = aiohttp.ClientSession()

        tasks = []

        for i, archive_row in enumerate(self.checking_range, start=self.starting_row_num):
            tasks.append(asyncio.create_task(self.check_video(i, archive_row)))

        await asyncio.gather(*tasks)
    
    async def check_videos_sync(self):
        self.session = aiohttp.ClientSession()

        for i, archive_row in enumerate(self.checking_range, start=self.starting_row_num):
            await self.check_video(i, archive_row)
    
    async def check_generic_async(self):
        self.session = aiohttp.ClientSession()

        tasks = []

        for i, row in enumerate(self.checking_range, start=self.starting_row_num):
            tasks.append(asyncio.create_task(self.check_link(i, row[0])))

        await asyncio.gather(*tasks)

    async def check_generic_sync(self):
        self.session = aiohttp.ClientSession()

        for i, row in enumerate(self.checking_range, start=self.starting_row_num):
            await self.check_link(i, row[0])

    def clamp_to_archive_range(self, e: Event):
        """Clamp values in the start and end entries to the range of the
        archive or generic list"""
        if self.checks_row_start_entry.cget("state") != tk.NORMAL:
            return
        
        generic = self.generic_list_var.get()
        start = self.checks_row_start_entry.get()
        end = self.checks_row_end_entry.get()

        if e.widget._name == "start":
            end = int(end)

            try:
                start = int(start)
            except:
                self.checks_row_start_entry.delete(0, tk.END)
                self.checks_row_start_entry.insert(0, 1 if generic else 2)
                self.videos_to_fetch = end - (1 if generic else 0)
                self.progress_label.config(text=f"Progress: 0/{self.videos_to_fetch} videos checked")
                return

            clamped = max(1 if generic else 2, min(start, end))

            if clamped != start:
                self.checks_row_start_entry.delete(0, tk.END)
                self.checks_row_start_entry.insert(0, clamped)

            self.videos_to_fetch = end - clamped + 1

        elif e.widget._name == "end":
            start = int(start)

            try:
                end = int(end)
            except:
                self.checks_row_end_entry.delete(0, tk.END)
                self.checks_row_end_entry.insert(0, len(self.checking_range if generic else self.archive_rows))
                self.videos_to_fetch = len(self.checking_range if generic else self.archive_rows) - start + 1
                self.progress_label.config(text=f"Progress: 0/{self.videos_to_fetch} videos checked")
                return
            
            clamped = max(start, min(end, len(self.archive_rows)))

            if clamped != end:
                self.checks_row_end_entry.delete(0, tk.END)
                self.checks_row_end_entry.insert(0, clamped)

            self.videos_to_fetch = clamped - start + 1
        
        self.progress_label.config(text=f"Progress: 0/{self.videos_to_fetch} videos checked")
