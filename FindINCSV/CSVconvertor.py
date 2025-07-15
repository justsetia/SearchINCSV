import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def convert_txt_to_utf8_csv():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask for the input .txt file (usually Excel Unicode Text)
    txt_path = filedialog.askopenfilename(title="Select Unicode Text file", filetypes=[("Text Files", "*.txt")])
    if not txt_path:
        print("No file selected.")
        return

    # Read the text file (Excel Unicode Text files are usually UTF-16 LE encoded with tab separators)
    try:
        df = pd.read_csv(txt_path, sep='\t', encoding='utf-16')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file:\n{e}")
        return

    # Ask where to save the CSV UTF-8
    save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV UTF-8", "*.csv")],
                                             title="Save as UTF-8 CSV")
    if not save_path:
        print("No save location selected.")
        return

    try:
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        messagebox.showinfo("Success", f"File saved successfully as UTF-8 CSV:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file:\n{e}")

if __name__ == "__main__":
    convert_txt_to_utf8_csv()
