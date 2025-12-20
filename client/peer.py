import os
import hashlib
import bencodepy
import random
import socket
import threading
import requests
import time
from urllib.parse import urlencode
from collections import defaultdict
import shutil

class Peer:
    def __init__(self, peer_id=None, port=6881):
        self.peer_id = peer_id or self.generate_peer_id()
        self.port = port
        self.shared_files = {}
        self.active_downloads = {}
        self.connections = defaultdict(dict)
        self.server_socket = None

    # ---------------- PEER ID ----------------
    def generate_peer_id(self):
        return "-PC0001-" + "".join(str(random.randint(0, 9)) for _ in range(12))

    # ---------------- CREATE TORRENT ----------------
    def create_torrent(self, file_path, tracker_url, piece_size=256 * 1024):
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found")

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        pieces = []
        with open(file_path, "rb") as f:
            while True:
                piece = f.read(piece_size)
                if not piece:
                    break
                pieces.append(hashlib.sha1(piece).digest())

        info = {
            b"name": file_name.encode(),
            b"length": file_size,
            b"piece length": piece_size,
            b"pieces": b"".join(pieces)
        }

        torrent_data = {
            b"announce": tracker_url.encode(),
            b"info": info
        }

        base = os.path.splitext(file_path)[0]
        torrent_path = base + ".torrent"

        with open(torrent_path, "wb") as f:
            f.write(bencodepy.encode(torrent_data))

        self.shared_files[file_name] = file_path
        return torrent_path

    # ---------------- SERVER (SEEDER) ----------------
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(5)

        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(
                target=self.handle_connection,
                args=(conn,),
                daemon=True
            ).start()

    def handle_connection(self, conn):
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
        finally:
            conn.close()

    # ---------------- DOWNLOAD ----------------
    def start_download(self, torrent_path):
        if not os.path.exists(torrent_path):
            raise FileNotFoundError("Torrent file not found")

        with open(torrent_path, "rb") as f:
            torrent = bencodepy.decode(f.read())

        info = torrent[b"info"]
        file_name = info[b"name"].decode()
        file_length = info[b"length"]

        os.makedirs("downloads", exist_ok=True)

        # MINI PROJECT LOGIC:
        # Copy from shared_files instead of real P2P chunking
        src = os.path.join("shared_files", file_name)
        dst = os.path.join("downloads", file_name)

        if not os.path.exists(src):
            raise Exception("Seeder file not found")

        shutil.copy(src, dst)

        return {
            "name": file_name,
            "length": file_length
        }
