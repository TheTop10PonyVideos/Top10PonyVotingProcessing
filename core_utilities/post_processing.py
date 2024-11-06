"""Post-processing application."""

import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font
from PIL import ImageTk, Image
from functions.post_processing import (
    fetch_videos_data,
    generate_top10_archive_records,
    generate_hm_archive_records,
    generate_sharable_records,
    generate_top10_archive_csv,
    generate_hm_archive_csv,
    generate_sharable_csv,
    generate_showcase_description,
)
from functions.top_10_parser import parse_calculated_top_10_csv
from functions.messages import suc, inf, err
from classes.gui import GUI

class PostProcessing(GUI):
    def gui(self, root):
        # Create application window
        root.title("Top 10 Pony Videos: Post-processing")
        root.geometry(f"800x400")

        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(Image.open("images/post-processing.png"))
        banner_label = tk.Label(main_frame, image=self.banner_image)
        banner_label.pack()

        # Create title
        title_font = Font(size=16)
        title_label = tk.Label(main_frame, font=title_font, text="Post-processing")
        title_label.pack(pady=8)

        # Create "Choose Input CSV..." control
        input_file_frame = tk.Frame(main_frame)
        input_file_label = tk.Label(input_file_frame, text="Input CSV file:")

        default_input_file = "outputs/calculated_top_10.csv"
        self.input_file_var = tk.StringVar()
        self.input_file_var.set(default_input_file)
        input_file_entry = ttk.Entry(input_file_frame, width=40, textvariable=self.input_file_var)

        browse_button = ttk.Button(
            input_file_frame, text="📁 Choose Input CSV...", command=self.browse_input_file
        )

        input_file_label.grid(column=0, row=0, padx=5, pady=5)
        input_file_entry.grid(column=1, row=0, padx=5, pady=5)
        browse_button.grid(column=2, row=0, padx=5, pady=5)

        input_file_frame.pack()

        # Create buttons bar
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack()

        run_button = ttk.Button(
            buttons_frame, text="🏁 Run Post-processing", command=self.handle_post_processing
        )
        run_button.grid(column=0, row=0, padx=5, pady=5)

        quit_button = ttk.Button(buttons_frame, text="Back to Main Menu", command=lambda: GUI.run("MainMenu", root))
        quit_button.grid(column=1, row=0, padx=5, pady=5)
    
    def browse_input_file(self):
        """Handler for the "Choose Input CSV" button. Opens a file dialog and sets the
        global variable `input_file_var` to the selected file."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.input_file_var.set(file_path)


    def handle_post_processing(self):
        """Handler for the "Run post-processing" button."""
        input_file_str = self.input_file_var.get()
        if input_file_str.strip() == "":
            tk.messagebox.showinfo("Error", "Please select a CSV file to process.")
            return

        input_file_path = Path(input_file_str)
        output_dir = "outputs"
        output_file_prefix = "post-processed-"

        calc_records = []
        with input_file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            required_header = ["Title", "Percentage", "Total Votes", "URL", "Notes"]
            if reader.fieldnames != required_header:
                err(
                    f'Selected CSV file "{input_file_str}" has an invalid header: {",".join(reader.fieldnames)}'
                )
                tk.messagebox.showinfo(
                    "Error",
                    f"The selected CSV file is invalid. The file must have the following header line:\n\n{','.join(required_header)}",
                )
                return

            calc_records = [record for record in reader]

        inf("Performing post-processing...")

        grouped_records = parse_calculated_top_10_csv(calc_records)

        top_10_records = grouped_records["Top 10"]
        hm_records = grouped_records["HONORABLE MENTIONS"]
        history_records = grouped_records["HISTORY"]

        top_10_video_urls = [record["URL"] for record in top_10_records]
        hm_video_urls = [record["URL"] for record in hm_records]

        history_video_url_groups = {
            anni_year: {r["URL"] for r in records}
            for anni_year, records in history_records.items()
        }
        history_video_urls = []
        for anni_year, group in history_video_url_groups.items():
            for url in group:
                history_video_urls.append(url)

        yt_api_key = GUI.yt_api_key_var.get()

        top_10_videos_data = fetch_videos_data(yt_api_key, top_10_video_urls)
        hm_videos_data = fetch_videos_data(yt_api_key, hm_video_urls)
        history_videos_data = fetch_videos_data(yt_api_key, history_video_urls)

        top10_archive_records = generate_top10_archive_records(top_10_records, top_10_videos_data)
        hm_archive_records = generate_hm_archive_records(hm_records, hm_videos_data)
        sharable_records = generate_sharable_records(top_10_records, hm_records)
        showcase_desc = generate_showcase_description(
            top_10_records,
            hm_records,
            history_records,
            top_10_videos_data,
            hm_videos_data,
            history_videos_data,
        )

        top10_archive_file = f"{output_dir}/{output_file_prefix}top10-archive.csv"
        hm_archive_file = f"{output_dir}/{output_file_prefix}hm-archive.csv"
        sharable_file = f"{output_dir}/{output_file_prefix}sharable.csv"
        desc_file = f"{output_dir}/{output_file_prefix}description.txt"

        generate_top10_archive_csv(top10_archive_records, top10_archive_file)
        suc(f"Wrote top 10 archive data to {top10_archive_file}.")
        generate_hm_archive_csv(hm_archive_records, hm_archive_file)
        suc(f"Wrote honorable mention archive data to {hm_archive_file}.")
        generate_sharable_csv(sharable_records, sharable_file)
        suc(f"Wrote sharable spreadsheet data to {sharable_file}.")

        with open(desc_file, "w", encoding="utf8") as file:
            file.write(showcase_desc)

        suc(f"Wrote showcase description to {desc_file}.")
        suc("Finished.")

        tk.messagebox.showinfo(
            "Success",
            f"Post-processing complete. The following output files have been created:\n\n{top10_archive_file}\n{hm_archive_file}\n{sharable_file}\n{desc_file}",
        )
