import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import chardet
import unicodedata
class CSVSearchApp:
    def __init__(self, Root):
        self.root = Root
        self.root.title("CSV Search Tool")
        self.csv_files = []

        # Upload button
        self.upload_btn = tk.Button(Root, text=" CSVآپلود فایل‌های ", command=self.upload_files)
        self.upload_btn.pack(pady=10)

        # Filter buttons (export single column)
        self.filter_frame = tk.Frame(Root)
        self.filter_frame.pack(pady=5)

        tk.Button(self.filter_frame, text="کد ملی", command=lambda: self.export_column("کد ملی")).pack(side=tk.LEFT, padx=5)
        tk.Button(self.filter_frame, text="شماره موبایل", command=lambda: self.export_column("شماره موبایل")).pack(side=tk.LEFT, padx=5)
        tk.Button(self.filter_frame, text="نام و نام خانوادگی", command=lambda: self.export_column("نام و نام خانوادگی")).pack(side=tk.LEFT, padx=5)

        # Search bar
        self.search_frame = tk.Frame(Root)
        self.search_frame.pack(pady=5)
        self.search_entry = tk.Entry(self.search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_button = tk.Button(self.search_frame, text="جستجو", command=self.search_csvs)
        self.search_button.pack(side=tk.LEFT)
        self.files_listbox = tk.Listbox(Root, height=5)
        self.files_listbox.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Results table (preview only)
        self.tree = ttk.Treeview(Root)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def normalize_text(self, text):
        text = unicodedata.normalize('NFC', str(text))
        text = text.replace('\u064A', '\u06CC')  # Arabic Yeh to Persian Yeh
        text = text.replace('\u0643', '\u06A9')  # Arabic Kaf to Persian Kaf
        return text

    def export_column(self, column_name):
        if not self.csv_files:
            print("No files uploaded.")
            return

        output_values = []
        chunk_size = 100_000

        for file in self.csv_files:
            try:
                for chunk in pd.read_csv(file, chunksize=chunk_size, encoding='utf-8-sig'):
                    if column_name in chunk.columns:
                        values = chunk[column_name].dropna().astype(str).apply(self.normalize_text)
                        output_values.extend(values.tolist())
            except Exception as e:
                print(f"Error reading {file}: {e}")

        if not output_values:
            print(f"No values found for column '{column_name}'.")
            return

        # Save to CSV with UTF-8 BOM (to fix messed up fonts in Excel)
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv")],
            title=f"Save values for '{column_name}'"
        )
        if save_path:
            pd.DataFrame({column_name: output_values}).to_csv(
                save_path, index=False, encoding='utf-8-sig'
            )
            print(f"{len(output_values)} values saved to {save_path}.")

    def upload_files(self):
        new_files = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        if not new_files:
            return

        import os
        # Add only files that aren't already loaded
        for file in new_files:
            if file not in self.csv_files:
                self.csv_files.append(file)
                self.files_listbox.insert(tk.END, os.path.basename(file))
        print(f"{len(new_files)} files added. Total files now: {len(self.csv_files)}")



    def search_csvs(self):
        query = self.search_entry.get()
        if not query or not self.csv_files:
            return

        # Normalize query and convert to lower
        query = self.search_entry.get()

        query = self.normalize_text(query).lower()
        print(f"Normalized query repr: {repr(query)}")
        print(f"Normalized query unicode points: {[hex(ord(c)) for c in query]}")


        results = []
        chunk_size = 100_000
        max_rows_per_file = 1_000_000

        for file in self.csv_files:
            try:
                for chunk in pd.read_csv(file, chunksize=chunk_size, encoding='utf-8-sig'):
                    print(f"Columns in chunk from file {file}: {chunk.columns.tolist()}")

                    # Normalize each cell and search
                    def row_matches(row):
                        for val in row.astype(str):
                            norm_val = self.normalize_text(val).lower()
                            if query in norm_val:
                                return True
                        return False

                    matches = chunk[chunk.apply(row_matches, axis=1)]

                    if not matches.empty:
                        results.append(matches)
            except Exception as e:
                print(f"Error processing {file}: {e}")

        # Clear the treeview (optional)
        for i in self.tree.get_children():
            self.tree.delete(i)

        if results:
            result_df = pd.concat(results, ignore_index=True)
            total_rows = len(result_df)

            folder_path = filedialog.askdirectory(title="Select folder to save output files")
            if not folder_path:
                print("No folder selected.")
                return

            num_parts = (total_rows // max_rows_per_file) + int(total_rows % max_rows_per_file != 0)

            for i in range(num_parts):
                start = i * max_rows_per_file
                end = min((i + 1) * max_rows_per_file, total_rows)
                part_df = result_df.iloc[start:end]
                output_path = f"{folder_path}/search_results_part_{i + 1}.csv"
                part_df.to_csv(output_path, index=False, encoding='utf-8-sig')
                print(f"Saved {end - start} rows to: {output_path}")

            print(f"Search completed successfully. {total_rows} matching rows saved in {num_parts} file(s).")
        else:
            print("No matches found for your query.")


def detect_encoding(file_path, sample_size=10000):
    with open(file_path, 'rb') as f:
        rawdata = f.read(sample_size)
    result = chardet.detect(rawdata)
    print(f"Detected encoding for {file_path}: {result['encoding']} with confidence {result['confidence']}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = CSVSearchApp(root)
    root.mainloop()
    detect_encoding("G:/Amn Nasr Inter/SearchFile/files/Test1.csv")
