import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .peer import Peer
import threading

class TorrentGUI:
    def __init__(self, root):
        self.root = root
        self.peer = None
        self.setup_gui()
        self.initialize_peer()

    def setup_gui(self):
        self.root.title("Mini Torrent Client")
        self.root.geometry("800x600")

        self.tab_control = ttk.Notebook(self.root)

        self.download_tab = ttk.Frame(self.tab_control)
        self.upload_tab = ttk.Frame(self.tab_control)
        self.status_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.download_tab, text='Downloads')
        self.tab_control.add(self.upload_tab, text='Uploads')
        self.tab_control.add(self.status_tab, text='Status')
        self.tab_control.pack(expand=1, fill="both")

        self.setup_download_tab()
        self.setup_upload_tab()
        self.setup_status_tab()

    # ---------------- DOWNLOAD TAB ----------------
    def setup_download_tab(self):
        ttk.Label(self.download_tab, text="Torrent File:").grid(row=0, column=0, padx=5, pady=5)
        self.torrent_path = tk.StringVar()
        ttk.Entry(self.download_tab, textvariable=self.torrent_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.download_tab, text="Browse", command=self.browse_torrent).grid(row=0, column=2)

        ttk.Button(self.download_tab, text="Start Download", command=self.start_download).grid(row=1, column=1, pady=10)

        self.download_tree = ttk.Treeview(
            self.download_tab,
            columns=('name', 'size', 'progress'),
            show='headings'
        )
        self.download_tree.heading('name', text='File Name')
        self.download_tree.heading('size', text='Size')
        self.download_tree.heading('progress', text='Progress')
        self.download_tree.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        self.download_tab.grid_rowconfigure(2, weight=1)
        self.download_tab.grid_columnconfigure(1, weight=1)

    # ---------------- UPLOAD TAB ----------------
    def setup_upload_tab(self):
        ttk.Label(self.upload_tab, text="File to Share:").grid(row=0, column=0, padx=5, pady=5)
        self.share_path = tk.StringVar()
        ttk.Entry(self.upload_tab, textvariable=self.share_path, width=50).grid(row=0, column=1)
        ttk.Button(self.upload_tab, text="Browse", command=self.browse_share_file).grid(row=0, column=2)

        ttk.Label(self.upload_tab, text="Tracker URL:").grid(row=1, column=0, padx=5)
        self.tracker_url = tk.StringVar(value="http://127.0.0.1:5000")
        ttk.Entry(self.upload_tab, textvariable=self.tracker_url, width=50).grid(row=1, column=1)

        ttk.Button(self.upload_tab, text="Create Torrent", command=self.create_torrent).grid(row=2, column=1, pady=10)

        self.upload_tree = ttk.Treeview(
            self.upload_tab,
            columns=('name', 'size'),
            show='headings'
        )
        self.upload_tree.heading('name', text='File Name')
        self.upload_tree.heading('size', text='Size')
        self.upload_tree.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

        self.upload_tab.grid_rowconfigure(3, weight=1)
        self.upload_tab.grid_columnconfigure(1, weight=1)

    # ---------------- STATUS TAB ----------------
    def setup_status_tab(self):
        ttk.Label(self.status_tab, text="Peer ID:").grid(row=0, column=0, padx=5, pady=5)
        self.peer_id_label = ttk.Label(self.status_tab, text="")
        self.peer_id_label.grid(row=0, column=1)

    def initialize_peer(self):
        self.peer = Peer(port=6881)
        self.peer_id_label.config(text=self.peer.peer_id)
        threading.Thread(target=self.peer.start_server, daemon=True).start()

    def browse_torrent(self):
        file = filedialog.askopenfilename(filetypes=[("Torrent files", "*.torrent")])
        if file:
            self.torrent_path.set(file)

    def browse_share_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.share_path.set(file)

    def create_torrent(self):
        file_path = self.share_path.get()
        tracker_url = self.tracker_url.get()

        if not file_path:
            messagebox.showerror("Error", "Select a file")
            return

        try:
            torrent = self.peer.create_torrent(file_path, tracker_url)
            messagebox.showinfo("Success", f"Torrent created: {torrent}")
            self.upload_tree.insert('', 'end', values=(
                os.path.basename(file_path),
                f"{os.path.getsize(file_path)/1024:.2f} KB"
            ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_download(self):
        torrent_file = self.torrent_path.get()
        if not torrent_file:
            messagebox.showerror("Error", "Select a torrent file")
            return

        try:
            info = self.peer.start_download(torrent_file)
            self.download_tree.insert('', 'end', values=(
                info['name'],
                f"{info['length']/1024:.2f} KB",
                "Completed"
            ))
            messagebox.showinfo("Success", "Download completed")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def run_gui():
    root = tk.Tk()
    TorrentGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
