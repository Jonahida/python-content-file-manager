import os
import tkinter as tk
from tkinter import filedialog, messagebox

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")

        # Directory path
        self.directory = tk.StringVar()
        # File extension, new extension, and number of characters (defaults)
        self.file_extension = tk.StringVar(value=".txt")
        self.new_extension = tk.StringVar(value=".svg")
        self.num_characters = tk.IntVar(value=100)

        # Directory selection
        tk.Label(root, text="Directory:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(root, textvariable=self.directory, width=50).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(root, text="Browse", command=self.browse_directory).grid(row=0, column=2, padx=10, pady=5)

        # Multi-line Text input for content matching
        tk.Label(root, text="Content to match:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.search_text_widget = tk.Text(root, width=50, height=5)
        self.search_text_widget.grid(row=1, column=1, padx=10, pady=5)
        self.search_text_widget.bind("<KeyRelease>", self.update_character_count)
        self.search_text_widget.bind("<Control-a>", self.select_all_text)  # Bind Control+A for select all
        self.search_text_widget.bind("<Control-v>", self.override_paste)  # Bind Control+V for override paste

        # File extension input
        tk.Label(root, text="File extension:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(root, textvariable=self.file_extension, width=10).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # New extension input
        tk.Label(root, text="New extension:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(root, textvariable=self.new_extension, width=10).grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Number of characters to read display
        tk.Label(root, text="Characters to read:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.num_characters_label = tk.Label(root, textvariable=self.num_characters)
        self.num_characters_label.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Rename and Delete buttons
        tk.Button(root, text="Search", command=self.search_only).grid(row=5, column=1, padx=10, pady=5)
        tk.Button(root, text="Rename extensions", command=self.confirm_rename).grid(row=6, column=1, padx=10, pady=10, sticky="w")
        tk.Button(root, text="Delete files", command=self.confirm_delete).grid(row=6, column=1, padx=10, pady=10, sticky="e")


    def search_only(self):
        matching_files = self.get_matching_files()
        count = len(matching_files)

        if count == 0:
            messagebox.showinfo("Search Result", "No matching files found.")
            return

        messagebox.showinfo(
            "Search Result",
            f"Found {count} matching files.\n\n"
            + "\n".join(matching_files[:10])
            + ("\n\n(...)" if count > 10 else "")
        )

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory.set(directory)

    def update_character_count(self, event=None):
        # Update the number of characters to read based on the current text length
        content = self.search_text_widget.get("1.0", tk.END).strip()
        self.num_characters.set(len(content))

    def select_all_text(self, event=None):
        # Select all text in the search_text_widget
        self.search_text_widget.tag_add("sel", "1.0", "end")
        return "break"  # Prevent default behavior

    def override_paste(self, event=None):
        # Clear the current content before pasting new content
        self.search_text_widget.delete("1.0", tk.END)
        # Schedule paste action after clearing the widget
        self.root.after(1, lambda: self.search_text_widget.event_generate("<<Paste>>"))
        return "break"  # Prevent default behavior

    def get_matching_files(self):
        folder = self.directory.get()
        search_text = self.search_text_widget.get("1.0", tk.END).strip()
        file_extension = self.file_extension.get() or ".txt"
        num_characters = self.num_characters.get()

        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid directory.")
            return []

        if not search_text:
            messagebox.showerror("Error", "Please enter text to match.")
            return []

        matching_files = []

        # 🔁 RECURSIVE SEARCH
        for root_dir, _, files in os.walk(folder):
            for filename in files:
                if not filename.endswith(file_extension):
                    continue

                file_path = os.path.join(root_dir, filename)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read(num_characters).lstrip()
                        if search_text in content:
                            matching_files.append(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

        return matching_files


    def confirm_rename(self):
        matching_files = self.get_matching_files()
        count = len(matching_files)
        
        if count == 0:
            messagebox.showinfo("Rename Files", "No matching files found.")
            return

        # Confirm with user
        if messagebox.askyesno("Confirm Rename", f"{count} files found. Do you want to rename them?"):
            self.rename_files(matching_files)
            self.clear_search_text()  # Clear after action

    def confirm_delete(self):
        matching_files = self.get_matching_files()
        count = len(matching_files)
        
        if count == 0:
            messagebox.showinfo("Delete Files", "No matching files found.")
            return

        # Confirm with user
        if messagebox.askyesno("Confirm Delete", f"{count} files found. Do you want to delete them?"):
            self.delete_files(matching_files)
            self.clear_search_text()  # Clear after action

    def clear_search_text(self):
        # Clear the content of the search_text_widget
        self.search_text_widget.delete("1.0", tk.END)
        self.num_characters.set(0)

    def rename_files(self, matching_files):
        count = 0
        new_extension = self.new_extension.get() if self.new_extension.get() else ".svg"
        for file_path in matching_files:
            new_path = file_path[:file_path.rfind(".")] + new_extension
            os.rename(file_path, new_path)
            count += 1

        messagebox.showinfo("Rename Complete", f"Renamed {count} files.")

    def delete_files(self, matching_files):
        count = 0
        for file_path in matching_files:
            os.remove(file_path)
            count += 1

        messagebox.showinfo("Delete Complete", f"Deleted {count} files.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()
