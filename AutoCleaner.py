"""
AutoCleaner.py

As version 1.852026, it only works with Shops Name available on July 2026, further use of this application requires updating 
the mapping in cleaning.py. Note that this is basically a name converter and grouping tool, not a full data cleaning tool. 
It is designed to be used in a simple workflow. YOU STILL NEED TO CHECK THE OUTPUT FILES MANUALLY FOR ERRORS AND INCONSISTENCIES.
if anything is wrong please try to understand the error code and try to fix it in cleaning.py, or should you require any assistance, 
please contact the developer (jayyidan1705@outlook.com).

This Application is strictly designed for internal use only, as it is highly specific to WMG's data and naming conventions.

HOW TO RUN IN TERMINAL
1. pip install pandas openpyxl python-calamine (firt time use only, if you have not installed these packages yet)
2. python AutoCleaner.py

Pick a file -> Run cleaning -> Save the result.

All actual cleaning logic lives in cleaning.py — this file is just the
window and the buttons.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext

from numpy import pad
import pandas as pd

from cleaning import process, unmatched_names


class CleaningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Name Cleaning Tool")
        self.root.geometry("520x320")
        self.root.resizable(False, False)

        self.input_path = None
        self.cleaned_df = None

        # 1. File selection row 
        tk.Label(root, text="Step 1: Select your file", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=15, pady=(15, 0)
        )

        file_frame = tk.Frame(root)
        file_frame.pack(fill="x", padx=15, pady=5)

        self.file_label = tk.Label(file_frame, text="No file selected", fg="gray", anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True)

        tk.Button(file_frame, text="Browse...", command=self.select_file).pack(side="right")

        #  2. Run button
        tk.Label(root, text="Step 2: Run cleaning", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=15, pady=(15, 0)
        )
        self.run_button = tk.Button(
            root, text="Run Cleaning", command=self.run_cleaning, state="disabled", height=2
        )
        self.run_button.pack(fill="x", padx=15, pady=5)

        #  3. Save button 
        tk.Label(root, text="Step 3: Save result", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=15, pady=(15, 0)
        )
        self.save_button = tk.Button(
            root, text="Save Cleaned File As...", command=self.save_file, state="disabled", height=2
        )
        self.save_button.pack(fill="x", padx=15, pady=5)

        #Status / log box
        tk.Label(root, text="Status", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=15, pady=(15, 0)
        )
        self.status_text = tk.Text(root, height=6, state="disabled", bg="#f5f5f5")
        self.status_text.pack(fill="both", padx=15, pady=(5, 15), expand=True)

    def log(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select a data file",
            filetypes=[("Excel/CSV files", "*.xlsx *.xls *.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        self.input_path = path
        self.file_label.config(text=os.path.basename(path), fg="black")
        self.run_button.config(state="normal")
        self.save_button.config(state="disabled")
        self.cleaned_df = None
        self.log(f"Selected file: {path}")

    def _read_data_file(self, path):
        """
        Read an Excel/CSV file into a DataFrame.

        Some xlsx files (often ones exported from ERP systems or non-Excel
        tools) have non-standard XML metadata, e.g. a 'WindowWidth' attribute
        where the spec expects 'windowWidth'. openpyxl (pandas' default
        engine) is case-sensitive and raises a TypeError on these files.
        When that happens, retry with the calamine engine, which is more
        tolerant of this kind of metadata quirk.
        """
        if path.lower().endswith(".csv"):
            return pd.read_csv(path)

        try:
            return pd.read_excel(path)
        except TypeError as e:
            if "WindowWidth" in str(e) or "windowWidth" in str(e):
                self.log("Standard reader failed on file metadata — retrying with a fallback reader...")
                return pd.read_excel(path, engine="calamine")
            raise

    def run_cleaning(self):
        try:
            df = self._read_data_file(self.input_path)

            if "Name" not in df.columns:
                messagebox.showerror(
                    "Missing column",
                    "This file has no 'Name' column. Please check the file and try again.",
                )
                self.log("ERROR: 'Name' column not found.")
                return

            self.cleaned_df = process(df, name_col="Name", group_col="group")

            missed = unmatched_names(self.cleaned_df, name_col="Name")
            self.log(f"Cleaning complete. {len(self.cleaned_df)} rows processed.")
            if missed:
                self.log(f"{len(missed)} name(s) not in the mapping (grouped as 'Other'):")
                for name in missed[:10]:
                    self.log(f"   - {name}")
                if len(missed) > 10:
                    self.log(f"   ...and {len(missed) - 10} more.")
            else:
                self.log("All names matched the mapping.")

            self.save_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error while cleaning", str(e))
            self.log(f"ERROR: {e}")


    def save_file(self):
        if self.cleaned_df is None:
            return

        path = filedialog.asksaveasfilename(
            title="Save cleaned file as",
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx"), ("CSV file", "*.csv")],
        )
        if not path:
            return

        try:
            if path.lower().endswith(".csv"):
                self.cleaned_df.to_csv(path, index=False)
            else:
                self.cleaned_df.to_excel(path, index=False)
            self.log(f"Saved to: {path}")
            messagebox.showinfo("Saved", f"File saved successfully:\n{path}")
        except Exception as e:
            messagebox.showerror("Error while saving", str(e))
            self.log(f"ERROR while saving: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CleaningApp(root)
    root.mainloop()