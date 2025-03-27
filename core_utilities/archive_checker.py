"""Application for checking the status of videos in the master archive."""

import tkinter as tk
import os, csv, json
import threading
import asyncio
import aiohttp

from tkinter import filedialog, Event, ttk
from PIL import ImageTk, Image
from typing import List, Tuple
from yt_dlp import YoutubeDL, DownloadError
from enum import Enum
from classes.typing import ArchiveRecord
from classes.gui import GUI
from data.globals import ydl_opts
from functions.general import (
    load_top_10_master_archive,
    load_honorable_mentions_archive
)
from functions.messages import inf


blocked_everywhere_indicator = "EVERYWHERE EXCEPT:"
video_not_found = "Video not found"
lock = asyncio.Lock()


class States(Enum):
    NON_EMBEDDABLE = ("non-embedable", "non-embeddable")
    UNAVAILABLE = ("unavailable", "deleted", "private", "tos deleted", "terminated")
    AGE_RESTRICTED = ("age-restricted",)
    BLOCKED = ("blocked",)

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
        self.var_use_local_archive = tk.BooleanVar(value=False)

    def gui(self, root):

        # Only load archive when it's not being checked so progress
        # label and output path is displayed properly upon revisiting
        if not self.running:
            self.archive_records = load_top_10_master_archive(self.var_use_local_archive.get())
            self.videos_to_fetch = len(self.archive_records)

        root.title("YouTube Video Status Checker")

        root.geometry("800x600")
        root.grid_columnconfigure(0, weight=1)

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(Image.open("images/archive-checker.png"))

        banner_label = tk.Label(root, image=self.banner_image, pady=5)
        self.input_file_frame = tk.Frame(root)
        output_file_frame = tk.Frame(root)
        settings_frame = tk.LabelFrame(root, text="Settings")
        run_frame = tk.Frame(root)
        info_frame = tk.Frame(root)

        banner_label.grid(column=0, row=0)
        self.input_file_frame.grid(column=0, row=1)
        output_file_frame.grid(column=0, row=2)
        settings_frame.grid(column=0, row=3, pady=5)
        run_frame.grid(column=0, row=4, pady=(10, 5))
        info_frame.grid(column=0, row=5)

        # Input File Frame
        self.var_generic_csv_input = tk.StringVar()

        # Output File Frame
        output_file_label = tk.Label(output_file_frame, text="Output CSV file:")

        self.default_output_file = "outputs/status_checker_results"

        if os.path.exists(f"{self.default_output_file}.csv"):
            i = 2

            while os.path.exists(f"{self.default_output_file}{i}.csv"):
                i += 1

            self.default_output_file = f"{self.default_output_file}{i}"

        self.default_output_file += ".csv"

        self.var_output_file = tk.StringVar(value=self.default_output_file)
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
        self.var_check_titles = tk.BooleanVar()
        self.var_async_requests = tk.BooleanVar(value=True)
        self.var_contrast_states = tk.BooleanVar(value=False)

        csv_range_frame = tk.Frame(settings_frame)

        check_titles = tk.Checkbutton(
            settings_frame,
            text="Check Title Differences",
            variable=self.var_check_titles,
        )

        # Kept optional for debugging
        use_async = tk.Checkbutton(
            settings_frame, text="Async Requests (faster)", variable=self.var_async_requests
        )

        contrast_states = tk.Checkbutton(
            settings_frame, text="Contrast States", variable=self.var_contrast_states
        )

        use_local_archive = tk.Checkbutton(
            settings_frame, text="Use Local Archive", variable=self.var_use_local_archive
        )

        checker_subject_frame = tk.Frame(settings_frame)

        csv_range_frame.grid(column=0, row=0, pady=4)
        check_titles.grid(column=0, row=1, padx=(35, 0), sticky="w")
        use_async.grid(column=0, row=2, padx=(35, 0), sticky="w")
        contrast_states.grid(column=0, row=3, padx=(35, 0), sticky="w")
        use_local_archive.grid(column=0, row=4, padx=(35, 0), sticky="w")
        checker_subject_frame.grid(column=0, row=5)

        # Settings Frame -> Range Frame
        range_label = tk.Label(csv_range_frame, text="Range")

        self.checks_row_start_entry = tk.Entry(csv_range_frame, name="start", width=10)
        self.checks_row_start_entry.bind("<Return>", self.clamp_to_archive_range)
        self.checks_row_start_entry.bind("<FocusOut>", self.clamp_to_archive_range)
        self.checks_row_start_entry.insert(
            0, self.starting_row_num if self.running else 2
        )
        self.checks_row_start_entry.config(
            state=tk.DISABLED if self.running else tk.NORMAL
        )

        self.checks_row_end_entry = tk.Entry(csv_range_frame, name="end", width=10)
        self.checks_row_end_entry.bind("<Return>", self.clamp_to_archive_range)
        self.checks_row_end_entry.bind("<FocusOut>", self.clamp_to_archive_range)
        self.checks_row_end_entry.insert(
            0,
            (
                self.starting_row_num + len(self.checking_range) - 1
                if self.running
                else len(self.archive_records) + 1
            ),
        )
        self.checks_row_end_entry.config(
            state=tk.DISABLED if self.running else tk.NORMAL
        )

        range_label.pack(padx=(5, 5), side="left")
        self.checks_row_start_entry.pack(padx=(5, 5), side="left")
        self.checks_row_end_entry.pack(padx=(5, 5))

        # Settings Frame -> Checker Subject Frame
        self.var_checker_subject = tk.StringVar(value="ma")

        master_archive = tk.Radiobutton(
            checker_subject_frame,
            text="Master\nArchive",
            value="ma",
            variable=self.var_checker_subject,
            command=self.change_checker_subject
        )
        honorable_mentions = tk.Radiobutton(
            checker_subject_frame,
            text="Honorable\nMentions",
            value="hm",
            variable=self.var_checker_subject,
            command=self.change_checker_subject
        )
        generic_list = tk.Radiobutton(
            checker_subject_frame,
            text="Generic\nList",
            value="gl",
            variable=self.var_checker_subject,
            command=self.change_checker_subject
        )

        master_archive.pack(side="left")
        honorable_mentions.pack(side="left")
        generic_list.pack()

        # Run Frame
        self.start_button = ttk.Button(
            run_frame,
            text="Run Status Checker",
            command=self.run_status_checker,
            state=tk.DISABLED if self.running else tk.NORMAL,
        )
        self.start_button.grid(column=0, row=0, padx=5, pady=5)

        quit_button = ttk.Button(
            run_frame,
            text="Back to Main Menu",
            command=lambda: GUI.run("MainMenu"),
        )
        quit_button.grid(column=1, row=0, padx=5, pady=5)

        # Info Frame
        self.progress_label = tk.Label(
            info_frame,
            text=f"Progress: {self.processed_videos if self.running else 0}/{self.videos_to_fetch} videos checked",
        )
        self.progress_label.grid(column=0, row=1, padx=3, pady=3)

        self.result_label = tk.Label(
            root,
            text=(
                self.output_csv_path
                if len(self.checking_range)
                and (self.processed_videos == len(self.checking_range))
                else ""
            ),
        )
        self.result_label.grid(column=0, row=6, pady=10)

    def change_checker_subject(self):
        """Called whenever a checker subject option is selected.
        Changes the ui to allow status checking the master archive,
        honorable metions archive, or a generic video list csv"""
        subject = self.var_checker_subject.get()

        if subject == "gl":
            tk.Label(self.input_file_frame, text="Input CSV File:").grid(
                column=0, row=0, padx=5
            )
            tk.Entry(
                self.input_file_frame,
                width=40,
                textvariable=self.var_generic_csv_input,
                state="readonly",
            ).grid(column=1, row=0, padx=5)
            ttk.Button(
                self.input_file_frame, text="📁 Choose...", command=self.browse_input_file
            ).grid(column=2, row=0, padx=5)
            self.input_file_frame.grid()

            self.checks_row_start_entry.delete(0, tk.END)
            self.checks_row_start_entry.config(state="readonly")
            self.checks_row_end_entry.delete(0, tk.END)
            self.checks_row_end_entry.config(state="readonly")
            self.start_button.config(state=tk.DISABLED)
            return self.progress_label.config(text="Progress: -/- videos checked")
        
        for child in self.input_file_frame.winfo_children():
            child.destroy()  # RIP childs again
        self.input_file_frame.grid_remove()

        if subject == "hm":
            self.archive_records = load_honorable_mentions_archive(self.var_use_local_archive.get())
        else:
            self.archive_records = load_top_10_master_archive(self.var_use_local_archive.get())

        self.videos_to_fetch = len(self.archive_records)

        self.checks_row_start_entry.config(state=tk.NORMAL)
        self.checks_row_start_entry.delete(0, tk.END)
        self.checks_row_start_entry.insert(0, 2)
        self.checks_row_end_entry.config(state=tk.NORMAL)
        self.checks_row_end_entry.delete(0, tk.END)
        self.checks_row_end_entry.insert(0, len(self.archive_records) + 1)
        self.progress_label.config(
            text=f"Progress: 0/{self.videos_to_fetch} videos checked"
        )
        self.start_button.config(state=tk.NORMAL)

    def browse_output_file(self):
        """Handler for the "Choose Output CSV" button. Opens a file dialog and sets the
        variable `var_output_file` to the selected file."""
        file_path = filedialog.asksaveasfilename(filetypes=[("CSV Files", "*.csv")])

        if file_path and not file_path.endswith(".csv"):
            file_path += ".csv"

        self.var_output_file.set(file_path if file_path else self.default_output_file)

    def browse_input_file(self):
        """Handler for the "Choose Input CSV" button. Opens a file dialog and sets the
        variable `var_generic_csv_input` to the selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        self.var_generic_csv_input.set(file_path)

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
            self.progress_label.config(
                text=f"Progress: 0/{self.videos_to_fetch} videos checked"
            )
            self.start_button.config(state=tk.NORMAL)

    def check_non_youtube_video_status(
        self, video_url
    ) -> Tuple[str, List[States], List[str]]:
        """Get the current state of a video using the yt-dlp module"""
        # Note: During debugging, no videos were found to have any bad status
        # Most of this was copilot generated since it'd be difficult or tedious
        # to check for each platforms edge cases. It's implementation could potentially
        # be inaccurate but in practice should be sufficient enough especially if
        # the debugger is used to manually check and update this code every once in a while

        try:
            states = []

            info_dict = self.ydl.extract_info(video_url, download=False)

            if info_dict.get("upload_date", None):
                visibility = info_dict.get("access_control", {}).get("form", "Public")
                video_title = info_dict.get("title")
                age_limit = info_dict.get("age_limit")
                availability = info_dict.get("availability")
                geo_restricted = info_dict.get("geo_restricted")
                content_rating = info_dict.get("content_rating")
                status = info_dict.get("status")

                # if status or content_rating:
                #    print(status, content_rating)

                if age_limit and age_limit >= 18:
                    states.append(States.AGE_RESTRICTED)

                blocked_countries = info_dict.get("blocked_countries", [])
                countries_where_a_significant_amount_of_bronies_probably_live_so_if_any_one_are_in_a_videos_banned_list_then_mark_it_as_blocked_oh_but_except_for_ones_that_are_known_for_blocking_a_lot_more_pony_videos = ["US", "GB", "DE", "FR", "IT", "ES", "NL", "BE", "SE", "NO", "DK", "FI", "AT", "CH", "PL", "PT", "GR", "CZ", "HU", "IE", "RO", "BG", "SK", "HR"]

                if (
                    geo_restricted
                    or (availability and "blocked" in availability)
                    or len(blocked_countries) >= 5
                    or any(country in countries_where_a_significant_amount_of_bronies_probably_live_so_if_any_one_are_in_a_videos_banned_list_then_mark_it_as_blocked_oh_but_except_for_ones_that_are_known_for_blocking_a_lot_more_pony_videos for country in blocked_countries)
                ):
                    states.append(States.BLOCKED)

                if visibility != "Public":
                    states.append(States.get(visibility))
            else:
                states.append(States.UNAVAILABLE)

            return video_title, states, blocked_countries
        except DownloadError:
            if "vimeo.com" in video_url:
                print(f"\n{video_url} requires a manual check\n")
                return "[COULDN'T FETCH VIMEO DATA]", [], []

            return video_not_found, [States.UNAVAILABLE], []

    async def check_youtube_video_status(
        self, video_id, tries=0
    ) -> Tuple[str, List[States], List[str]]:
        """Get the current state of a video using the Youtube Data API"""
        try:
            async with self.session.get(
                f"https://www.googleapis.com/youtube/v3/videos?key={self.youtube_api_key}&id={video_id}&part=snippet,contentDetails,status"
            ) as response:
                response = json.loads(await response.text())

                if response.get("items"):
                    states = []

                    item = response["items"][0]
                    video_title = item["snippet"]["title"]
                    status_info = item.get("status", {})
                    video_details = item["contentDetails"]

                    if not status_info.get("embeddable"):
                        states.append(States.NON_EMBEDDABLE)

                    if (
                        video_details.get("contentRating", {}).get("ytRating")
                        == "ytAgeRestricted"
                    ):
                        states.append(States.AGE_RESTRICTED)

                    region_restriction = video_details.get("regionRestriction", {})

                    countries_where_a_significant_amount_of_bronies_probably_live_so_if_any_one_are_in_a_videos_banned_list_then_mark_it_as_blocked_oh_but_except_for_ones_that_are_known_for_blocking_a_lot_more_pony_videos = ["US", "GB", "DE", "FR", "IT", "ES", "NL", "BE", "SE", "NO", "DK", "FI", "AT", "CH", "PL", "PT", "GR", "CZ", "HU", "IE", "RO", "BG", "SK", "HR"]

                    blocked_countries: list = (
                        [blocked_everywhere_indicator]
                        + region_restriction.get("allowed")
                        if "allowed" in region_restriction
                        else region_restriction.get("blocked", [])
                    )
                    if len(blocked_countries) >= 5 or "allowed" in region_restriction or any(country in countries_where_a_significant_amount_of_bronies_probably_live_so_if_any_one_are_in_a_videos_banned_list_then_mark_it_as_blocked_oh_but_except_for_ones_that_are_known_for_blocking_a_lot_more_pony_videos for country in blocked_countries):
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
            video_id = (
                video_url.split("v=")[-1]
                if "youtube.com" in video_url
                else video_url.split("/")[-1]
            )
            updated_video_title, video_states, blocked_countries = (
                await self.check_youtube_video_status(video_id)
            )

        else:
            updated_video_title, video_states, blocked_countries = (
                self.check_non_youtube_video_status(video_url)
            )
            blocked_countries = []

        if updated_video_title == video_not_found:
            updated_video_title = video_title

        return updated_video_title, video_states, blocked_countries

    def write_to_output_csv(self):
        """Writes the discrepancies from the list of notes into a csv file"""
        header = [
            "",
            "Archive Row",
            "Video URL",
            "Video Title",
            "Video Status",
            "Blocked Countries",
        ]
        with open(self.output_csv_path, "w", encoding="utf-8") as output_csvfile:
            csv_writer = csv.writer(output_csvfile, lineterminator="\n")

            if not self.var_checker_subject.get():
                csv_writer.writerow(header)

            csv_writer.writerows(self.updated_rows)

        if self == GUI.active_gui and self.ready:
            self.result_label.config(
                text=f"Output CSV saved at: {self.output_csv_path}"
            )

    # Increment the progress counter and signal when the checking process is done
    async def update_progress(self):
        """Increment the displayed progress label, and close the aiohttp session
        when all videos have been processed"""
        self.processed_videos += 1
        if self == GUI.active_gui and self.ready:
            self.progress_label.config(
                text=f"Progress: {self.processed_videos}/{self.videos_to_fetch} videos checked"
            )

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
        self.youtube_api_key = GUI.get_api_key()
        if not self.youtube_api_key: return

        output_file_dir = self.var_output_file.get()
        if not output_file_dir:
            return

        self.output_csv_path = output_file_dir

        if "cookiefile" not in ydl_opts:
            inf("Note: Couldn't find data/cookies.txt file. Some requests may yield no data.")
        self.ydl = YoutubeDL(ydl_opts)
        checker_subject = self.var_checker_subject.get()

        self.starting_row_num = int(self.checks_row_start_entry.get())

        if checker_subject == "gl":
            self.checking_range = self.checking_range[
                self.starting_row_num - 1 : int(self.checks_row_end_entry.get())
            ]
        else:
            self.checking_range = self.archive_records[
                self.starting_row_num - 2 : int(self.checks_row_end_entry.get()) - 1
            ]

        self.updated_rows = []
        self.processed_videos = 0
        self.check_titles = self.var_check_titles.get()

        # Run the check_videos function in a separate thread
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.checks_row_start_entry.config(state=tk.DISABLED)
        self.checks_row_end_entry.config(state=tk.DISABLED)

        if checker_subject == "gl":
            if self.var_async_requests.get():
                threading.Thread(
                    target=lambda: self.async_loop.run_until_complete(
                        self.check_generic_async()
                    )
                ).start()
            else:
                threading.Thread(
                    target=lambda: asyncio.run(self.check_generic_sync())
                ).start()
        else:
            if self.var_async_requests.get():
                threading.Thread(
                    target=lambda: self.async_loop.run_until_complete(
                        self.check_videos_async()
                    )
                ).start()
            else:
                threading.Thread(
                    target=lambda: asyncio.run(self.check_videos_sync())
                ).start()

    async def check_video(self, row_index: int, archive_record: ArchiveRecord):
        """Compare the current state of a video with its corresponding archive entry, and note
        differences in states. Also checks the alt link when appropriate"""
        initial_states = (
            archive_record["state"].split("/")
            if len(archive_record["state"].split("/")) != 1
            else archive_record["state"].split(" & ")
        )
        initial_states = [
            States.get(state) for state in initial_states if States.get(state) != None
        ]

        video_title = archive_record["title"]
        video_url = archive_record.get("link", archive_record["alternate_link"])

        fetched_video_title, video_states, blocked_countries = (
            await self.get_video_status(video_url, video_title)
        )

        updated = False

        # This lock makes sure that line breaks and related items appended to updated_rows stay consistent
        async with lock:
            needs_updating = (
                (
                    (self.check_titles and (video_title != fetched_video_title))
                    or (
                        (
                            len(blocked_countries) >= 5
                            or blocked_everywhere_indicator in blocked_countries
                        )
                        and States.BLOCKED not in initial_states
                    )
                    or (
                        any(
                            video_state not in initial_states
                            for video_state in video_states
                        )
                    )
                    or (
                        any(
                            archive_state not in video_states
                            for archive_state in initial_states
                        )
                    )
                )
                if self.var_contrast_states.get()
                else (
                    (self.check_titles and (video_title != fetched_video_title))
                    or (bool(len(video_states)) != bool(len(initial_states)))
                )
            )

            if needs_updating:
                self.updated_rows.append(
                    [
                        "Current",
                        row_index,
                        video_url,
                        video_title,
                        archive_record["state"],
                        "",
                    ]
                )
                self.updated_rows.append(
                    [
                        "Updated",
                        row_index,
                        video_url,
                        fetched_video_title if self.check_titles else video_title,
                        (
                            " & ".join(
                                map(lambda state: state.value[0], tuple(video_states))
                            )
                            if video_states
                            else ""
                        ),
                        (
                            ", ".join(blocked_countries)
                            if States.BLOCKED in video_states
                            else ""
                        ),
                    ]
                )
                updated = True

            if (len(video_states) or len(initial_states)) and archive_record["alternate_link"]:
                video_url = archive_record["alternate_link"]

                _, video_states, blocked_countries = await self.get_video_status(
                    video_url, video_title
                )

                alt_useable = _ and not (
                    len(video_states)
                    or len(blocked_countries) >= 5
                    or (
                        len(blocked_countries) < 5
                        and States.BLOCKED in video_states
                        and blocked_everywhere_indicator not in blocked_countries
                    )
                )

                if (
                    _
                    and alt_useable
                    and archive_record["found"].lower() == "needed"
                ):
                    self.updated_rows.append(
                        [
                            "NOTE",
                            row_index,
                            video_url,
                            "ALT LINK IS USEABLE BUT LABELED 'needed'",
                            (
                                " & ".join(
                                    map(
                                        lambda state: state.value[0],
                                        tuple(video_states),
                                    )
                                )
                                if video_states
                                else ""
                            ),
                            (
                                ", ".join(blocked_countries)
                                if States.BLOCKED in video_states
                                else ""
                            ),
                        ]
                    )
                    updated = True
                elif (
                    _
                    and not alt_useable
                    and archive_record["found"].lower() != "needed"
                    and not (
                        States.AGE_RESTRICTED in video_states
                        and "age restriction" in archive_record["notes"]
                    )
                ):
                    self.updated_rows.append(
                        [
                            "NOTE",
                            row_index,
                            video_url,
                            "ALT LINK NOT USEABLE",
                            (
                                " & ".join(
                                    map(
                                        lambda state: state.value[0],
                                        tuple(video_states),
                                    )
                                )
                                if video_states
                                else ""
                            ),
                            (
                                ", ".join(blocked_countries)
                                if States.BLOCKED in video_states
                                else ""
                            ),
                        ]
                    )
                    updated = True

            if updated:
                self.updated_rows.append([""] * 6)

            await self.update_progress()

    async def check_link(self, row_index, video_url):
        """Check the video status of a video link, and create a note if it has a bad state"""
        fetched_video_title, video_states, blocked_countries = (
            await self.get_video_status(video_url, "")
        )

        if (
            len(blocked_countries) >= 5
            or blocked_everywhere_indicator in blocked_countries
        ):
            video_states.append(States.BLOCKED)

        # This lock makes sure that line breaks and related items appended to updated_rows stay consistent
        async with lock:
            if len(video_states):
                self.updated_rows.append(
                    [
                        "Bad Status",
                        row_index,
                        video_url,
                        fetched_video_title,
                        " & ".join(
                            map(lambda state: state.value[0], tuple(video_states))
                        ),
                        (
                            ", ".join(blocked_countries)
                            if States.BLOCKED in video_states
                            else ""
                        ),
                    ]
                )
                self.updated_rows.append([""] * 6)

            await self.update_progress()

    async def check_videos_async(self):
        self.session = aiohttp.ClientSession()

        tasks = []

        for i, archive_record in enumerate(
            self.checking_range, start=self.starting_row_num
        ):
            tasks.append(asyncio.create_task(self.check_video(i, archive_record)))

        await asyncio.gather(*tasks)

    async def check_videos_sync(self):
        self.session = aiohttp.ClientSession()

        for i, archive_row in enumerate(
            self.checking_range, start=self.starting_row_num
        ):
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

        generic = self.var_checker_subject.get()
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
                self.progress_label.config(
                    text=f"Progress: 0/{self.videos_to_fetch} videos checked"
                )
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
                self.checks_row_end_entry.insert(
                    0, len(self.checking_range) if generic else len(self.archive_records) + 1
                )
                self.videos_to_fetch = (
                    len(self.checking_range if generic else self.archive_records)
                    - start
                    + 1
                )
                self.progress_label.config(
                    text=f"Progress: 0/{self.videos_to_fetch} videos checked"
                )
                return

            clamped = max(start, min(end, len(self.archive_records) + 1))

            if clamped != end:
                self.checks_row_end_entry.delete(0, tk.END)
                self.checks_row_end_entry.insert(0, clamped)

            self.videos_to_fetch = clamped - start + 1

        self.progress_label.config(
            text=f"Progress: 0/{self.videos_to_fetch} videos checked"
        )
