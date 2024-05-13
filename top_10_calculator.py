import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font
from PIL import ImageTk, Image
from functions.top_10_calc import analyze_and_write_titles_to_csv
from functions.messages import suc, inf, err


def browse_input_file():
    """Handler for the "Choose Input CSV" button. Opens a file dialog and sets the
    global variable `input_file_var` to the selected file."""
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    input_file_var.set(file_path)


def handle_calc():
    """Handler for the "Calculate Top 10" button."""
    input_csv_path = input_file_var.get()
    if input_csv_path.strip() == "":
        tk.messagebox.showinfo("Error", "Please select a CSV file.")
        return

    inf("Performing Top 10 calculation...")

    output_csv_path = "outputs/calculated_top_10.csv"
    analyze_and_write_titles_to_csv(input_csv_path, output_csv_path)
    suc(f"Wrote calculated rankings to {output_csv_path}.")
    suc("Finished.")

    tk.messagebox.showinfo(
        "Success",
        f"Top 10 calculation complete. A file containing the video rankings has been created at:\n\n{output_csv_path}"
    )


# Create application window
root = tk.Tk()
root.title("Top 10 Pony Videos: Top 10 Calculator")
root.geometry(f"800x400")

# Create main frame
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

# Create banner image
banner_image = ImageTk.PhotoImage(Image.open("images/top-10-calc-ts.png"))
banner_label = tk.Label(main_frame, image=banner_image)
banner_label.pack()

# Create title
title_font = Font(size=16)
title_label = tk.Label(main_frame, font=title_font, text="Top 10 Calculator")
title_label.pack(pady=8)

# Create "Choose Input CSV..." control
input_file_frame = tk.Frame(main_frame)
input_file_label = tk.Label(input_file_frame, text="Input CSV file:")

default_input_file = "outputs/processed.csv"
input_file_var = tk.StringVar()
input_file_var.set(default_input_file)
input_file_entry = ttk.Entry(input_file_frame, width=40, textvariable=input_file_var)

browse_button = ttk.Button(
    input_file_frame, text="📁 Choose Input CSV...", command=browse_input_file
)

input_file_label.grid(column=0, row=0, padx=5, pady=5)
input_file_entry.grid(column=1, row=0, padx=5, pady=5)
browse_button.grid(column=2, row=0, padx=5, pady=5)

input_file_frame.pack()

# Create buttons bar
buttons_frame = tk.Frame(main_frame)
buttons_frame.pack()

run_button = ttk.Button(
    buttons_frame, text="🧮 Calculate Top 10", command=handle_calc
)
run_button.grid(column=0, row=0, padx=5, pady=5)

quit_button = ttk.Button(buttons_frame, text="Quit", command=root.destroy)
quit_button.grid(column=1, row=0, padx=5, pady=5)

root.mainloop()
