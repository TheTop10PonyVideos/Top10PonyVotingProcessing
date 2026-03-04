"""Application for checking the status of videos in the master archive."""

import tkinter as tk
import csv, json
import pandas as pd
import threading
import asyncio
import aiohttp

from tkinter import filedialog, Event, ttk
from PIL import ImageTk, Image
from yt_dlp import YoutubeDL, DownloadError
from classes.typing import ArchiveRecord, StatusRow
from classes.enums import VideoState, CSVType
from classes.gui import GUI
from data.globals import ydl_opts
from functions.archive import (
    load_top_10_master_archive,
    load_honorable_mentions_archive
)
from functions.messages import inf


blocked_everywhere_indicator = "EVERYWHERE EXCEPT:"

class ArchiveStatusChecker(GUI):
    def __init__(self):
        super().__init__()
        self.default_output_file = "outputs/status_checker_results.csv"

        self.var_checker_target     = tk.StringVar()
        self.var_output_file        = tk.StringVar(value=self.default_output_file)
        self.var_input_file_generic = tk.StringVar()
        self.var_use_local_archive  = tk.BooleanVar()
        self.var_check_titles       = tk.BooleanVar()
        self.var_async              = tk.BooleanVar(value=True)

        self.reset_vars()
    
    def reset_vars(self):
        self.processed_rows = 0
        self.starting_row_num = 2
        self.ydl = None
        self.output_csv_path = ""
        self.archive_records = []
        self.checking_range = []
        self.results: list[StatusRow] = []

        self.var_checker_target.set(CSVType.MASTER_ARCHIVE.value)

    def gui(self, root):
        self.archive_records = load_top_10_master_archive(self.var_use_local_archive.get())
        self.num_to_fetch = len(self.archive_records)

        root.title("YouTube Video Status Checker")

        root.geometry("800x600")
        root.grid_columnconfigure(0, weight=1)

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(Image.open("images/archive-checker.png"))

        banner_label = tk.Label(root, image=self.banner_image, pady=5)
        self.input_file_frame = tk.Frame(root)
        output_file_frame = tk.Frame(root)
        settings_frame = tk.LabelFrame(root, text="Settings")
        frame_quit_run = tk.Frame(root)
        frame_info = tk.Frame(root)
        self.label_result = tk.Label(root, text="")

        banner_label.grid(column=0, row=0)
        self.input_file_frame.grid(column=0, row=1)
        output_file_frame.grid(column=0, row=2)
        settings_frame.grid(column=0, row=3, pady=5)
        frame_quit_run.grid(column=0, row=4, pady=(10, 5))
        frame_info.grid(column=0, row=5)
        self.label_result.grid(column=0, row=6, pady=8)

        # Output File Frame
        output_file_label = tk.Label(output_file_frame, text="Output CSV file:")

        output_file_entry = tk.Entry(
            output_file_frame, width=40, textvariable=self.var_output_file
        )

        browse_button = ttk.Button(
            output_file_frame, text="📁 Choose...", command=self.browse_output_file
        )

        output_file_label.grid(column=0, row=0, padx=5)
        output_file_entry.grid(column=1, row=0, padx=5)
        browse_button.grid(column=2, row=0, padx=5)

        # Settings Frame
        csv_range_frame = tk.Frame(settings_frame)

        check_titles = tk.Checkbutton(
            settings_frame,
            text="Check Title Differences",
            variable=self.var_check_titles,
        )

        # Kept optional for debugging
        use_async = tk.Checkbutton(
            settings_frame, text="Async Requests (faster)", variable=self.var_async
        )

        use_local_archive = tk.Checkbutton(
            settings_frame, text="Use Local Archive", variable=self.var_use_local_archive
        )

        checker_subject_frame = tk.Frame(settings_frame)

        csv_range_frame.grid(column=0, row=0, pady=4)
        check_titles.grid(column=0, row=1, padx=(35, 0), sticky="w")
        use_async.grid(column=0, row=2, padx=(35, 0), sticky="w")
        use_local_archive.grid(column=0, row=3, padx=(35, 0), sticky="w")
        checker_subject_frame.grid(column=0, row=4)

        # Settings Frame -> Range Frame
        range_label = tk.Label(csv_range_frame, text="Range")

        self.entry_checks_row_start = tk.Entry(csv_range_frame, name="start", width=10)
        self.entry_checks_row_start.bind("<Return>", self.clamp_to_archive_range)
        self.entry_checks_row_start.bind("<FocusOut>", self.clamp_to_archive_range)
        self.entry_checks_row_start.insert(0, 2)

        self.entry_checks_row_end = tk.Entry(csv_range_frame, name="end", width=10)
        self.entry_checks_row_end.bind("<Return>", self.clamp_to_archive_range)
        self.entry_checks_row_end.bind("<FocusOut>", self.clamp_to_archive_range)
        self.entry_checks_row_end.insert(0, len(self.archive_records) + 1)

        range_label.pack(padx=(5, 5), side="left")
        self.entry_checks_row_start.pack(padx=(5, 5), side="left")
        self.entry_checks_row_end.pack(padx=(5, 5))

        # Settings Frame -> Checker Subject Frame
        self.radio_master_archive = tk.Radiobutton(
            checker_subject_frame,
            text="Master\nArchive",
            value=CSVType.MASTER_ARCHIVE.value,
            variable=self.var_checker_target,
            command=self.checker_target_changed
        )
        self.radio_honorable_mentions = tk.Radiobutton(
            checker_subject_frame,
            text="Honorable\nMentions",
            value=CSVType.HONORABLE_MENTIONS.value,
            variable=self.var_checker_target,
            command=self.checker_target_changed
        )
        self.radio_generic_list = tk.Radiobutton(
            checker_subject_frame,
            text="Generic\nList",
            value=CSVType.GENERIC_LIST.value,
            variable=self.var_checker_target,
            command=self.checker_target_changed
        )

        self.radio_master_archive.pack(side="left")
        self.radio_honorable_mentions.pack(side="left")
        self.radio_generic_list.pack()

        # Run Frame
        self.btn_start = ttk.Button(
            frame_quit_run,
            text="Run Status Checker",
            command=self.run_status_checker,
        )

        self.btn_quit = ttk.Button(
            frame_quit_run,
            text="Back to Main Menu",
            command=self.quit
        )

        self.btn_start.grid(column=0, row=0, padx=5, pady=5)
        self.btn_quit.grid(column=1, row=0, padx=5, pady=5)

        # Info Frame
        self.label_progress = tk.Label(
            frame_info,
            text=f"Progress: {0}/{self.num_to_fetch} videos checked",
        )
        self.label_progress.grid(column=0, row=1, padx=3, pady=3)

    def checker_target_changed(self):
        """Adjusts the ui to facilitate checking each kind of video list,
        honorable metions archive, or a generic video list csv"""
        target = CSVType(self.var_checker_target.get())

        if target is CSVType.GENERIC_LIST:
            tk.Label(self.input_file_frame, text="Input CSV File:").grid(
                column=0, row=0, padx=5
            )
            tk.Entry(
                self.input_file_frame,
                width=40,
                textvariable=self.var_input_file_generic,
                state="readonly",
            ).grid(column=1, row=0, padx=5)
            ttk.Button(
                self.input_file_frame, text="📁 Choose...", command=self.browse_input_file
            ).grid(column=2, row=0, padx=5)
            self.input_file_frame.grid()

            self.entry_checks_row_start.delete(0, tk.END)
            self.entry_checks_row_start.config(state="readonly")
            self.entry_checks_row_end.delete(0, tk.END)
            self.entry_checks_row_end.config(state="readonly")
            self.btn_start.config(state=tk.DISABLED)
            return self.label_progress.config(text="Progress: -/- videos checked")
        
        for child in self.input_file_frame.winfo_children():
            child.destroy()  # RIP childs again
        self.input_file_frame.grid_remove()

        use_local = self.var_use_local_archive.get()
        self.archive_records = (
            load_top_10_master_archive(use_local)
            if target is CSVType.MASTER_ARCHIVE 
            else load_honorable_mentions_archive(use_local)
        )

        self.processed_rows = 0
        self.num_to_fetch = len(self.archive_records)

        self.entry_checks_row_start.config(state=tk.NORMAL)
        self.entry_checks_row_start.delete(0, tk.END)
        self.entry_checks_row_start.insert(0, 2)
        self.entry_checks_row_end.config(state=tk.NORMAL)
        self.entry_checks_row_end.delete(0, tk.END)
        self.entry_checks_row_end.insert(0, len(self.archive_records) + 1)
        self.label_progress.config(
            text=f"Progress: 0/{self.num_to_fetch} videos checked"
        )
        self.btn_start.config(state=tk.NORMAL)

    def ui_lock(self, val: bool):
        state = tk.DISABLED if val else tk.NORMAL

        self.entry_checks_row_start.config(state=state)
        self.entry_checks_row_end.config(state=state)

        self.radio_master_archive.config(state=state)
        self.radio_honorable_mentions.config(state=state)
        self.radio_generic_list.config(state=state)

        self.btn_start.config(state=state)
        self.btn_quit.config(state=state)

    def browse_output_file(self):
        """Handler for the "Choose Output CSV" button. Opens a file dialog and sets the
        variable `var_output_file` to the selected file."""
        file_path = (
            filedialog.asksaveasfilename(filetypes=[("CSV Files", "*.csv")])
            or self.default_output_file
        )

        if not file_path.endswith(".csv"):
            file_path += ".csv"

        self.var_output_file.set(file_path)

    def browse_input_file(self):
        """Handler for the "Choose Input CSV" button. Opens a file dialog and sets the
        variable `var_generic_csv_input` to the selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        self.var_input_file_generic.set(file_path)

        if not file_path:
            self.entry_checks_row_start.delete(0, tk.END)
            self.entry_checks_row_start.config(state="readonly")
            self.entry_checks_row_end.delete(0, tk.END)
            self.entry_checks_row_end.config(state="readonly")
            self.btn_start.config(state=tk.DISABLED)
            self.label_progress.config(text="Progress: -/- videos checked")
            return

        with open(file_path, "r", encoding="utf-8") as input_csv_file:
            csv_reader = csv.reader(input_csv_file)
            self.checking_range = [row[0] for row in csv_reader]
            self.num_to_fetch = len(self.checking_range)

            self.entry_checks_row_start.config(state=tk.NORMAL)
            self.entry_checks_row_start.delete(0, tk.END)
            self.entry_checks_row_start.insert(0, 1)
            self.entry_checks_row_end.config(state=tk.NORMAL)
            self.entry_checks_row_end.delete(0, tk.END)
            self.entry_checks_row_end.insert(0, self.num_to_fetch)
            self.label_progress.config(
                text=f"Progress: 0/{self.num_to_fetch} videos checked"
            )
            self.btn_start.config(state=tk.NORMAL)

    async def get_video_status(self, video_url) -> tuple[str | None, set[VideoState] | None, list[str]]:
        """Get the current status of a video by requesting its data using the youtube data api or ytdlp.
        Returns None in place of the set of video states when an unexpected error occurs"""
        notable_countries = ["US", "GB", "DE", "FR", "IT", "ES", "NL", "BE", "SE", "NO", "DK", "FI", "AT", "CH", "PL", "PT", "GR", "CZ", "HU", "IE", "RO", "BG", "SK", "HR"]
        states = set()
        video_title = None
        blocked_countries = []

        if "youtube.com" in video_url or "youtu.be" in video_url:
            video_id = (
                video_url.split("v=")[-1]
                if "youtube.com" in video_url
                else video_url.split("/")[-1]
            )

            try:
                async with self.session.get(
                    f"https://www.googleapis.com/youtube/v3/videos?key={self.youtube_api_key}&id={video_id}&part=snippet,contentDetails,status"
                ) as response:
                    response = json.loads(await response.text())

                if not len(response.get("items", [])):
                    return None, set([VideoState.UNAVAILABLE]), []

                item = response["items"][0]
                video_title = item["snippet"]["title"]
                status_info = item.get("status", {})
                video_details = item["contentDetails"]

                if not status_info.get("embeddable"):
                    states.add(VideoState.NON_EMBEDDABLE)

                if (
                    video_details.get("contentRating", {}).get("ytRating") == "ytAgeRestricted"
                ):
                    states.add(VideoState.AGE_RESTRICTED)

                region_restriction = video_details.get("regionRestriction", {})

                blocked_countries: list = (
                    [blocked_everywhere_indicator]
                    + region_restriction.get("allowed")
                    if "allowed" in region_restriction
                    else region_restriction.get("blocked", [])
                )
                if len(blocked_countries) >= 5 or "allowed" in region_restriction or any(country in notable_countries for country in blocked_countries):
                    states.add(VideoState.BLOCKED)                
            
            except Exception as e:
                if e.resp.status == 404:
                    return None, set([VideoState.UNAVAILABLE]), []
                
                return None, None, []

        elif "derpibooru.org" in video_url:
            return None, None, [] # TODO

        else:
            try:
                info_dict = self.ydl.extract_info(video_url, download=False)

                if info_dict.get("upload_date") is None:
                    return None, set([VideoState.UNAVAILABLE]), []

                visibility = info_dict.get("access_control", {}).get("form", "Public")
                video_title = info_dict.get("title")
                age_limit = info_dict.get("age_limit")
                availability = info_dict.get("availability")
                geo_restricted = info_dict.get("geo_restricted")
                content_rating = info_dict.get("content_rating")
                status = info_dict.get("status")

                if age_limit and age_limit >= 18:
                    states.add(VideoState.AGE_RESTRICTED)

                blocked_countries = info_dict.get("blocked_countries", [])

                if (
                    geo_restricted
                    or (availability and "blocked" in availability)
                    or len(blocked_countries) >= 5
                    or any(country in notable_countries for country in blocked_countries)
                ):
                    states.add(VideoState.BLOCKED)

                if visibility != "Public":
                    states.add(VideoState.get(visibility))
            except DownloadError:
                if "vimeo.com" in video_url:
                    print(f"\n{video_url} requires a manual check\n")
                    return None, None, []

        return video_title, states, blocked_countries

    def progress_loop(self):
        """Update the progress label every few milliseconds from the main thread.
        Writes the output data and unlocks the ui once all videos are checked"""
        self.label_progress.config(
            text=f"Progress: {self.processed_rows}/{self.num_to_fetch} videos checked"
        )

        if self.processed_rows == self.num_to_fetch:
            df = pd.DataFrame(self.results)
            df = df[[ # Reordering
                col for col in StatusRow.__annotations__.keys()
                if col in df.columns
            ]]
            df.columns = [" ".join(name.split("_")).title() for name in df.columns]
            df.to_csv(self.output_csv_path, index=False)

            self.label_result.config(text=f"Output CSV saved at: {self.output_csv_path}")

            self.ui_lock(False)
            return
        
        self.root.after(15, self.progress_loop)

    # The starting point for the main part of this process
    def run_status_checker(self):
        """Check the status of the archive or generic list and output a csv
        file of discrepancies or bad links respectively"""
        self.youtube_api_key = GUI.get_api_key()
        if not self.youtube_api_key: return

        output_file_dir = self.var_output_file.get()
        if not output_file_dir:
            return

        self.output_csv_path = output_file_dir

        if "cookiefile" not in ydl_opts:
            inf("Note: Couldn't find data/cookies.txt file. Some requests may yield no data.")

        if self.ydl is None:
            self.ydl = YoutubeDL(ydl_opts)

        self.starting_row_num = int(self.entry_checks_row_start.get())
        self.processed_rows = 0
        self.check_titles = self.var_check_titles.get()
        self.ui_lock(True)

        # Run the video checking in a separate thread and start a loop that updates the ui based on its progress
        threading.Thread(
            target=lambda: asyncio.run(self.check_videos(not self.var_async.get()))
        ).start()

        self.progress_loop()

    async def archived_status_check(self, row_index: int, archive_record: ArchiveRecord):
        """Compare the current state of a video with its corresponding archive entry, and note
        differences in states. Also checks the alt link when appropriate"""
        initial_states = (
            archive_record["state"].split("/")
            if len(archive_record["state"].split("/")) != 1
            else archive_record["state"].split(" & ")
        )

        initial_states = set(
            state
            for state_str in initial_states
            if (state := VideoState.get(state_str)) is not None
        )

        video_title = archive_record["title"]
        video_url = archive_record.get("link", archive_record["alternate_link"])

        fetched_video_title, video_states, blocked_countries = await self.get_video_status(video_url)

        if video_states is None:
            result["note"] = "Unexpected error on main url"
            self.results.append(result)
            self.processed_rows += 1
            return

        result: StatusRow = {
            "row": row_index,
            "url": video_url,
            "title": video_title,
        }

        if initial_states != video_states:
            result["prev_status"] = archive_record["state"]
            result["new_status"] = " & ".join(map(lambda state: state.value[0], video_states))
            result["blocked_countries"] = ", ".join(blocked_countries)

        if self.check_titles:
            result["new_title"] = fetched_video_title if video_title != fetched_video_title else ''

        if len(video_states) and archive_record["alternate_link"]:
            alt_url = archive_record["alternate_link"]

            alt_title, alt_states, alt_blocked_countries = await self.get_video_status(alt_url)

            if alt_states is None:
                result["note"] = "Unexpected error on alt url"
                self.results.append(result)
                self.processed_rows += 1
                return

            if not len(alt_states) and archive_record["found"].lower() == "needed":
                result["note"] = "ALT LINK USEABLE BUT LABELED 'needed'"

            elif (
                len(alt_states)
                and archive_record["found"].lower() != "needed"
                and not (
                    alt_states == set([VideoState.AGE_RESTRICTED])
                    and "age restriction" in archive_record["notes"] # Assuming fine if the alt link to bypass age restriction is in notes
                )
            ):
                result["note"] = f"ALT LINK LABELED  '{archive_record["found"].lower()}' BUT HAS {' & '.join(map(lambda state: state.value[0], alt_states))}"
            
            if result.get("note") is not None and initial_states == video_states:
                result["prev_status"] = archive_record["state"]
                result["new_status"] = "No Change"


        if len(result) > 3:
            self.results.append(result)

        self.processed_rows += 1

    async def generic_status_check(self, row_index, video_url):
        """Check the video status of a video, and create a note if it has a bad state"""
        if not video_url:
            self.processed_rows += 1
            return

        video_title, video_states, blocked_countries = await self.get_video_status(video_url)

        if len(video_states):
            self.results.append({
                "row": row_index,
                "url": video_url,
                "title": video_title,
                "new_status": " & ".join(map(lambda state: state.value[0], video_states)),
                "blocked_countries": ", ".join(blocked_countries)
            })

        self.processed_rows += 1

    async def check_videos(self, sequential):
        self.session = aiohttp.ClientSession()

        target = CSVType(self.var_checker_target.get())

        if target is CSVType.GENERIC_LIST:
            self.checking_range = self.checking_range[
                self.starting_row_num - 1 : int(self.entry_checks_row_end.get())
            ]
        else:
            self.checking_range = self.archive_records[
                self.starting_row_num - 2 : int(self.entry_checks_row_end.get()) - 1
            ]

        checking_func = self.generic_status_check if target is CSVType.GENERIC_LIST else self.archived_status_check

        # Checks the videos in the same order as the rows in the input csv
        if sequential:
            for i, row in enumerate(self.checking_range, start=self.starting_row_num):
                await checking_func(i, row)

        else:
            # Checks videos asynchronously so no time is wasted waiting for each request to receive a response
            tasks = [
                asyncio.create_task(checking_func(i, row))
                for i, row in enumerate(self.checking_range, start=self.starting_row_num)
            ]
            await asyncio.gather(*tasks)

        await self.session.close()

    def clamp_to_archive_range(self, e: Event):
        """Clamp values in the start and end entries to the range of the
        archive or generic list"""
        if self.entry_checks_row_start.cget("state") != tk.NORMAL:
            return

        generic = self.var_checker_target.get()
        start = self.entry_checks_row_start.get()
        end = self.entry_checks_row_end.get()

        if e.widget._name == "start":
            end = int(end)

            try:
                start = int(start)
            except:
                self.entry_checks_row_start.delete(0, tk.END)
                self.entry_checks_row_start.insert(0, 1 if generic else 2)
                self.num_to_fetch = end - (1 if generic else 0)
                self.label_progress.config(
                    text=f"Progress: 0/{self.num_to_fetch} videos checked"
                )
                return

            clamped = max(1 if generic else 2, min(start, end))

            if clamped != start:
                self.entry_checks_row_start.delete(0, tk.END)
                self.entry_checks_row_start.insert(0, clamped)

            self.num_to_fetch = end - clamped + 1

        elif e.widget._name == "end":
            start = int(start)

            try:
                end = int(end)
            except:
                self.entry_checks_row_end.delete(0, tk.END)
                self.entry_checks_row_end.insert(
                    0, self.num_to_fetch if generic else len(self.archive_records) + 1
                )
                self.num_to_fetch = (
                    len(self.checking_range if generic else self.archive_records)
                    - start
                    + 1
                )
                self.label_progress.config(
                    text=f"Progress: 0/{self.num_to_fetch} videos checked"
                )
                return

            clamped = max(start, min(end, len(self.archive_records) + 1))

            if clamped != end:
                self.entry_checks_row_end.delete(0, tk.END)
                self.entry_checks_row_end.insert(0, clamped)

            self.num_to_fetch = clamped - start + 1

        self.label_progress.config(
            text=f"Progress: 0/{self.num_to_fetch} videos checked"
        )
    
    def quit(self):
        if self.ydl is not None:
            self.ydl.close()
        
        self.reset_vars()

        GUI.run("MainMenu")
