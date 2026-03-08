"""Leaderboard process. Generates the creator leaderboard seen at the end of Top
10 Pony Videos showcases. The leaderboard is calculated using the data in the
master archive spreadsheet[1], which records the placements of each creator for
each month and year.

[1]: https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E
"""

from datetime import datetime
from pathlib import Path
import csv, json
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font
from PIL import ImageTk, Image
from functions.leaderboard import (
    calc_leaderboard,
    compare_leaderboards,
    get_year_months_with_vote_data,
)
from functions.archive import load_top_10_master_archive, merge_aliased_creators
from functions.messages import inf
from classes.gui import GUI
from classes.month_year import MonthYear

class Leaderboard(GUI):
    col_spacing = 10
    row_colors = ("#614267", "#7e6082")
    month_names = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    aliases_path = "data/creator_aliases.json"
    output_dir = "outputs"

    def __init__(self):
        super().__init__()

        self.master_archive = None
        # List of all creators whose leaderboard results are the merger of two
        # or more creators.
        self.merged_creators: list[str] = None
        # Dictionary which maps creators to a list of their aliases.
        self.aliases: list[list[str]] = None

        self.latest_data_label = None
        self.warning = None
        self.board_title = None
        self.board_subtitle = None
        self.canvas = None
        self.month_picker = None
        self.year_picker = None

        self.var_use_local_archive = tk.BooleanVar(value=False)
        self.var_month = tk.StringVar()
        self.var_year = tk.StringVar()
        self.var_period_months = tk.StringVar(value="12")

    def gui(self, root):
        # Create application window
        root.title("Top 10 Pony Videos: Leaderboard")
        win_width = 1000
        win_height = 600
        root.geometry(f"{win_width}x{win_height}")

        title_font = Font(size=16)
        small_font = Font(size=8)

        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        sidebar_frame = tk.Frame(main_frame)
        board_frame = tk.Frame(main_frame)
        sidebar_frame.grid(row=0, column=0, sticky=tk.N, padx=5)
        board_frame.grid(row=0, column=1)

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(Image.open("images/leaderboard.png"))
        banner_label = tk.Label(sidebar_frame, image=self.banner_image)
        banner_label.grid(row=0, column=0)

        # Add refresh local archive button
        refresh_archive = tk.Button(
            sidebar_frame,
            text="Refresh local archive",
            command=self.refresh_local_archive,
        )
        self.latest_data_label = tk.Label(sidebar_frame, text="Latest data: ", font=small_font)

        refresh_archive.grid(row=1, column=0)
        self.latest_data_label.grid(row=2, column=0)

        # Add controls frame to sidebar
        controls_frame = tk.Frame(sidebar_frame)
        controls_frame.grid(row=3, column=0, pady=5)

        use_local_archive = tk.Checkbutton(
            controls_frame, text="Use Local Archive", variable=self.var_use_local_archive
        )

        # Add month/year pickers
        self.month_picker = ttk.Combobox(
            controls_frame,
            textvariable=self.var_month,
            values=Leaderboard.month_names,
            width=5,
        )
        self.year_picker = ttk.Combobox(
            controls_frame,
            textvariable=self.var_year,
            width=5,
        )

        for picker in [
            self.month_picker,
            self.year_picker,
        ]:
            # Prevent user from editing the text values of the pickers, but
            # allow them to make selections from the available options.
            picker.state(["!disabled", "readonly"])

            # Detect when the combobox value is changed. This uses the
            # <<ComboboxSelected>> virtual event which is supplied by the ttk
            # module, which seems to be the only way to do it (the
            # validatecommand property doesn't seem to work). See the tkinter
            # docs[1] for more info.
            # [1]: https://docs.python.org/3/library/tkinter.ttk.html#virtual-events
            picker.bind("<<ComboboxSelected>>", lambda x: self.update_leaderboard())

        # Add an entry field for selecting the period.
        period_field = ttk.Spinbox(
            controls_frame,
            textvariable=self.var_period_months,
            command=lambda: self.update_leaderboard(),
            width=5,
            from_=1,
            to=120,
            increment=1,
        )

        date_picker_label = tk.Label(controls_frame, text="Leaderboard date:", anchor=tk.W)
        period_label = tk.Label(controls_frame, text="Period (months):", anchor=tk.W)
        date_picker_label.grid(row=2, column=0, sticky=tk.EW)
        self.month_picker.grid(row=2, column=1)
        self.year_picker.grid(row=2, column=2)
        period_label.grid(row=3, column=0, sticky=tk.EW)
        period_field.grid(row=3, column=1)

        # Add a warning below the period.
        self.warning = tk.Label(sidebar_frame, font=small_font, fg="#ff0000")
        self.warning.grid(row=4, column=0)

        # Add some handlers to the period field, so that we can detect when it's
        # been changed.
        period_field.bind("<KeyPress-Return>", lambda x: self.update_leaderboard())
        period_field.bind("<FocusOut>", lambda x: self.update_leaderboard())

        self.board_title = tk.Label(board_frame, font=title_font, text="Leaderboard")
        self.board_subtitle = tk.Label(board_frame, text="")
        self.board_title.grid(row=0, column=0)
        self.board_subtitle.grid(row=1, column=0)

        # Add leaderboard canvas and scrollbars
        #scrollbar_x = tk.Scrollbar(board_frame, orient=tk.HORIZONTAL)
        scrollbar_y = tk.Scrollbar(board_frame, orient=tk.VERTICAL)
        canvas_w = win_width * 0.6
        canvas_h = win_height * 0.7
        self.canvas = tk.Canvas(
            board_frame,
            yscrollcommand=scrollbar_y.set,
            width=canvas_w,
            height=canvas_h,
        )

        scrollbar_y.config(command=self.canvas.yview)

        self.canvas.grid(row=2, column=0)
        scrollbar_y.grid(row=2, column=1, sticky=tk.NS)

        # Add "Export to CSV" button
        export_csv_button = ttk.Button(
            sidebar_frame,
            text="📁 Export to CSV",
            command=self.export_to_csv,
        )
        export_csv_button.grid(row=5, column=0)
        
        # Add quit button
        quit_button = ttk.Button(
            main_frame,
            text="Back to Main Menu",
            command=lambda: GUI.run("MainMenu"),
        )
        quit_button.grid(row=1, column=0, padx=5, pady=5)

        self.init_leaderboard()
        self.update_leaderboard()

    def init_leaderboard(self):
        """Load the master archive (from the local file, if available) and
        initialize the leaderboard interface."""
        with open(Leaderboard.aliases_path) as aliases_file:
            self.aliases = json.load(aliases_file)
        self.master_archive = load_top_10_master_archive()
        self.merged_creators = merge_aliased_creators(self.master_archive, self.aliases)
        self.refresh_controls(True)

    def get_datepicker_date(self) -> tuple[MonthYear, int]:
        """Read the current datepicker selection and return a useful
        representation of the date. Also return the data period."""
        month_name = self.var_month.get()
        year = int(self.var_year.get())
        period = int(self.var_period_months.get())

        month_idx = Leaderboard.month_names.index(month_name)
        month_year = MonthYear(month_idx + 1, year)

        return month_year, period

    def update_leaderboard(self):
        """Calculate the current state of the leaderboard (based on the
        datepicker selections) and update the display."""
        month_year, period = self.get_datepicker_date()
        prev_month_year = month_year - 1

        # Get leaderboard, and the one we're comparing to
        leaderboard = calc_leaderboard(self.master_archive, month_year.month, month_year.year, period)
        prev_leaderboard = calc_leaderboard(self.master_archive, prev_month_year.month, prev_month_year.year, period)

        # Get the difference between the leaderboards
        leaderboard_diff = compare_leaderboards(prev_leaderboard, leaderboard)

        # Get the first and last month-years in the period. Note that the last
        # month-year is included in the period (i.e. a 12-month period ending in
        # Dec will have its first month in January, which is 11 months prior)
        first_data_month_year = month_year - period + 1
        f_data_m = first_data_month_year.month_name()
        f_data_y = first_data_month_year.year
        last_data_month_year = month_year
        l_data_m = last_data_month_year.month_name()
        l_data_y = last_data_month_year.year

        # For each month in the data period, check if the master archive has
        # vote share data available for it. If it doesn't, warn the user that
        # the leaderboard is being based on incomplete data.
        yms_with_data = get_year_months_with_vote_data(self.master_archive)
        mys_with_no_data = []
        for i in range(period):
            my = month_year - i
            if (my.year, my.month) not in yms_with_data:
                mys_with_no_data.append(my)

        if len(mys_with_no_data) > 0:
            s = ("", "has") if len(mys_with_no_data) == 1 else ("s", "have")
            self.warning.config(text=f"Warning: {len(mys_with_no_data)} month{s[0]} in the given\nperiod {s[1]} no vote share data.")
        else:
            self.warning.config(text="")

        self.board_title.config(text=f"Leaderboard - {month_year.month_name()} {month_year.year}")
        self.board_subtitle.config(text=f"Total vote share over {period} months ({f_data_m} {f_data_y} - {l_data_m} {l_data_y})")

        # Create table header
        header = [
            "Rank",
            "Creator",
            "Rank change", # Old rank
            "<blank>", # ->
            "<blank>", # New rank
            "<diff>", # Rank diff
            "Vote share change", # Old vote share
            "<blank>", # ->
            "<blank>", # New vote share
            "<diff>", # Vote share diff
        ]

        table = [header]

        # Sort the creators by their rank in the current month's leaderboard.
        # Creators who only appear on last month's leaderboard are ignored as
        # they no longer form part of the rankings.
        sorted_creators = sorted(leaderboard, key=lambda c: leaderboard_diff[c]["new_rank"])

        for i, creator in enumerate(sorted_creators):
            diff = leaderboard_diff[creator]
            rank = diff["new_rank"]
            old_rank = "-" if diff["old_rank"] is None else diff["old_rank"]
            new_rank = "-" if diff["new_rank"] is None else diff["new_rank"]
            rank_diff = "-" if diff["rank_diff"] is None else diff["rank_diff"]
            old_vote_share = f"{diff['old_vote_share']:.2f}"
            new_vote_share = f"{diff['new_vote_share']:.2f}"

            row = [
                rank,
                self.leaderboard_name(creator),
                old_rank,
                "→",
                new_rank,
                str(rank_diff),
                old_vote_share,
                "→",
                new_vote_share,
                f"{diff['vote_share_diff']:.2f}",
            ]
            if len(row) != len(header):
                raise Exception(f"Can't create leaderboard table - header has {len(header)} fields but row has {len(row)} fields")

            table.append(row)

        self.draw_table(table, [1.5, 1, 1, 1, 1, 1.5, 1, 1, 1, 1.5])

    def draw_table(self, table: list[list], col_w_mults: list[float]=None):
        """Draw a table to the leaderboard canvas. Sometimes columns are too
        thin to contain either the heading or their data - if this is the case,
        use col_w_mults to specify multipliers for column widths to make some
        wider as needed."""
        normal_font = Font(size=9)
        bold_font = Font(weight="bold", size=10)
        large_font = Font(weight="bold", size=16)

        # Canvas helpers
        def wipe_canvas():
            for obj_id in self.canvas.find_all():
                self.canvas.delete(obj_id)
        def make_bold(obj_id):
            self.canvas.itemconfigure(text_id, font=bold_font)

        # If there aren't any data columns (which can happen if no months in the
        # selected period have any data), display a message on the canvas.
        if len(table) == 1:
            wipe_canvas()
            canvas_w = int(self.canvas.cget("width"))
            canvas_h = int(self.canvas.cget("height"))
            bg = Leaderboard.row_colors[0]
            self.canvas.create_rectangle(0, 0, canvas_w, canvas_h, fill=bg, outline="")
            self.canvas.config(scrollregion=(0, 0, canvas_w, canvas_h))

            no_data_msg = "No data for this period."
            text_id = self.canvas.create_text(canvas_w / 2, canvas_h / 2, text=no_data_msg, fill="#ffffff")
            self.canvas.itemconfigure(text_id, font=large_font)
            return

        # Start by pre-drawing every text item in the table and measuring the
        # bounding box of each one. This tells us how much space is needed for
        # each column. (These drawn items won't be kept, they're just for
        # measuring).
        columns = [[] for col in table[0]]
        cell_heights = []
        for j, row in enumerate(table):
            for i, cell in enumerate(row):
                text_id = self.canvas.create_text(0, 0, text=cell)
                self.canvas.itemconfigure(text_id, font=normal_font)
                if j == 0:
                    make_bold(text_id)
                bbox = self.canvas.bbox(text_id)
                cell_w = bbox[2] - bbox[0]
                cell_h = bbox[3] - bbox[1]

                columns[i].append(cell_w)
                cell_heights.append(cell_h)

        # Calculate the row height and column widths for each column. Each
        # column should be wide enough to fit its widest data element, plus a
        # small buffer for spacing. The header row is ignored, as we plan to let
        # header cells span multiple columns.
        row_height = max(cell_heights)

        data_cols = [col[1:] for col in columns]
        col_widths = []
        col_widths = [max(col) for col in data_cols]
        col_widths = [w + Leaderboard.col_spacing for w in col_widths]

        # Apply column width multipliers if provided
        if col_w_mults is not None:
            if len(col_w_mults) != len(col_widths):
                raise Exception(f"Cannot draw table - there are {len(col_widths)}, columns but {len(col_w_mults)} column width multipliers were provided")
            col_widths = [w * col_w_mults[i] for i, w in enumerate(col_widths)]

        # Wipe canvas
        wipe_canvas()

        # Resize the canvas and scroll region to fit all rows and columns
        total_w = sum(col_widths) 
        total_h = row_height * len(table)
        self.canvas.config(scrollregion=(0, 0, total_w, total_h), width=total_w)

        # Update the header to remove directives (e.g. <blank>, <diff>), and
        # record which columns are using the directives.
        header = table[0]
        diff_col_idxs = [i for i,h in enumerate(header) if h == "<diff>"]
        table[0] = ["" if h == "<blank>" else h for h in table[0]]
        table[0] = ["" if h == "<diff>" else h for h in table[0]]

        # Draw table cells on canvas
        for j, row in enumerate(table):
            row_h = row_height
            x = 0
            y = j * row_h
            row_color = Leaderboard.row_colors[j%2]

            # Draw cell backgrounds
            for i, cell in enumerate(row):
                col_w = col_widths[i]
                rect_id = self.canvas.create_rectangle(x, y, x+col_w, y+row_h, fill=row_color, outline="")
                x += col_widths[i]

            x = 0

            # Draw cell contents
            for i, cell in enumerate(row):
                col_w = col_widths[i]
                text_id = self.canvas.create_text(x, y, text=cell, fill="#ffffff", anchor=tk.NW)
                self.canvas.itemconfigure(text_id, font=normal_font)

                # Make header row bold
                if j == 0:
                    make_bold(text_id)
                x += col_widths[i]

                # Make items in "Change" columns bold and color appropriately
                if i in diff_col_idxs:
                    make_bold(text_id)
                    change = None
                    try:
                        change = float(cell)

                        if change > 0:
                            self.canvas.itemconfigure(text_id, text=f"⇧ {cell}")
                            self.canvas.itemconfigure(text_id, fill="#00ff00")
                        elif change < 0:
                            assert cell.startswith("-")
                            self.canvas.itemconfigure(text_id, text=f"⇩ {cell[1:]}")
                            self.canvas.itemconfigure(text_id, fill="#ff6050")
                        elif change == 0:
                            self.canvas.itemconfigure(text_id, text=f"")
                    except ValueError:
                        pass

    def refresh_local_archive(self):
        """Force a new copy of the master archive to be downloaded and saved to
        disk."""
        self.master_archive = load_top_10_master_archive(False)

        # Reloading the master archive undoes any previous merging of aliased
        # creators, so repeat the merge.
        self.merged_creators = merge_aliased_creators(self.master_archive, self.aliases)
        self.refresh_controls()

    def refresh_controls(self, auto_select_date: bool=False):
        """Refresh the controls (especially the date pickers) so that they
        reflect the current state of the master archive. This is needed if an
        archive refresh is forced, as the date pickers may still be reflecting
        the previous archive state.

        If auto_select_date is True, the date pickers will be set to the most
        recent date for which vote share data is available."""
        # Get all years for which we have vote share data, and update the year
        # pickers with those years. Years are in reverse-chronological order in
        # the archive, but we put them in chronological order for the picker.
        year_months = get_year_months_with_vote_data(self.master_archive)
        years = []
        for year, month in year_months:
            if year not in years:
                years.append(year)
        year_strs = [str(y) for y in years]
        year_strs.reverse()
        self.year_picker.config(values=year_strs)

        # Update the "Latest data" label
        latest_data_year = year_months[0][0]
        latest_data_month = year_months[0][1]
        latest_data_month_name = Leaderboard.month_names[latest_data_month-1]

        self.latest_data_label.config(text=f"Latest data: {latest_data_month_name} {latest_data_year}")

        # Auto-select the month and year pickers if requested
        if auto_select_date:
            self.var_month.set(value=latest_data_month_name)
            self.var_year.set(value=latest_data_year)

    def calc_leaderboard_csv(self):
        """Calculate the current state of the leaderboard (based on the
        datepicker selections) and generate a CSV representation of it. The CSV
        representation is different to the one displayed on the canvas."""
        month_year, period = self.get_datepicker_date()
        prev_month_year = month_year - 1

        # Get leaderboard, and the one we're comparing to
        leaderboard = calc_leaderboard(self.master_archive, month_year.month, month_year.year, period)
        prev_leaderboard = calc_leaderboard(self.master_archive, prev_month_year.month, prev_month_year.year, period)

        # Get the difference between the leaderboards
        leaderboard_diff = compare_leaderboards(prev_leaderboard, leaderboard)

        # Create table header
        header = [
            "Rank",
            "Creator",
            "Previous month's rank",
            "Rank change",
            "Previous month's vote share",
            "Vote share",
            "Vote share change",
            "Vote share (rounded)",
            "Vote share change (rounded)",
            "Merged from multiple aliases",
            "Date",
            "Period (months)"
        ]
        table = [header]

        # Sort the creators by their rank in the current month's leaderboard.
        # Creators who only appear on last month's leaderboard are ignored as
        # they no longer form part of the rankings.
        sorted_creators = sorted(leaderboard, key=lambda c: leaderboard_diff[c]["new_rank"])

        for i, creator in enumerate(sorted_creators):
            diff = leaderboard_diff[creator]
            old_rank = "" if diff["old_rank"] is None else diff["old_rank"]
            rank_diff = "" if diff["rank_diff"] is None else diff["rank_diff"]
            is_merged = "yes" if creator in self.merged_creators else "no"
                    
            row = [
                str(diff["new_rank"]),
                self.leaderboard_name(creator),
                str(old_rank),
                str(rank_diff),
                f"{diff['old_vote_share']:.2f}",
                f"{diff['new_vote_share']:.2f}",
                f"{diff['vote_share_diff']:.2f}",
                round(diff['new_vote_share']),
                round(diff['vote_share_diff']),
                is_merged,
                str(month_year),
                period,
            ]
            if len(row) != len(header):
                raise Exception(f"Can't create leaderboard table - header has {len(header)} fields but row has {len(row)} fields")

            table.append(row)

        return table

    def export_to_csv(self):
        """Save the current leaderboard table to a csv file."""
        file_name = f"leaderboard-{self.var_month.get()}-{self.var_year.get()}-comp-p{self.var_period_months.get()}.csv"
        output_path = Path(Leaderboard.output_dir) / file_name
        table = self.calc_leaderboard_csv()
        with output_path.open("w", encoding="utf-8") as output_csv_file:
            csv_writer = csv.writer(output_csv_file, lineterminator="\n")
            csv_writer.writerows(table)
            tk.messagebox.showinfo("Export complete", f"Leaderboard exported to {output_path}")

    def leaderboard_name(self, creator: str) -> str:
        """Return the creator's name as it should be displayed on the
        leaderboard. For most creators this is just their name, for creators
        with multiple aliases, this is their main name followed by their
        aliases, separated by slashes."""
        if creator in self.merged_creators:
            names = [creator]
            names.extend(self.aliases[creator])
            return "/".join(names)

        return creator

