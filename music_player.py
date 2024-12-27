import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
from mutagen.mp3 import MP3
import threading
import time


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Methfy")
        self.root.geometry("1150x750")
        self.root.configure(bg="#1A2C2B")  # Koyu yeşil-turkuaz tonlarında arka plan

        pygame.mixer.init()
        self.playlist = []
        self.current_song_index = 0
        self.is_paused = False
        self.is_playing = False

        # Tema Renkleri
        primary_color = "#00ADB5"  # Turkuaz
        accent_color = "#00FFAB"   # Antep yeşili
        bg_color = "#1A2C2B"       # Arka plan rengi
        text_color = "#E6F4F1"     # Açık beyazımsı metin rengi

        # ttk Stilleri
        style = ttk.Style()
        style.configure("TButton", background=primary_color, foreground="white", font=("Arial", 12), borderwidth=0)
        style.map("TButton", background=[("active", accent_color)])
        style.configure("TLabel", background=bg_color, foreground=text_color, font=("Arial", 10))
        style.configure("TFrame", background=bg_color)
        style.configure("TProgressbar", troughcolor="#1A3E3A", background=accent_color)

        # Yan Çerçeve (Menü)
        self.sidebar = tk.Frame(self.root, bg=bg_color, width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.logo_label = tk.Label(self.sidebar, text="Methfy", font=("Arial", 20, "bold"), bg=bg_color, fg=primary_color)
        self.logo_label.pack(pady=20)

        self.add_button = ttk.Button(self.sidebar, text="Şarkı Ekle", command=self.add_to_playlist)
        self.add_button.pack(pady=10)

        self.playlist_box = tk.Listbox(self.sidebar, bg="#112F2E", fg=text_color, font=("Arial", 12), width=30, height=20, selectbackground=accent_color)
        self.playlist_box.pack(pady=10)

        # Ana Çerçeve
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Şarkı Bilgileri
        self.song_label = ttk.Label(self.main_frame, text="Şu Anda Çalıyor: -", font=("Arial", 16, "bold"))
        self.song_label.pack(pady=10)

        self.song_length_label = ttk.Label(self.main_frame, text="00:00 / 00:00", font=("Arial", 12))
        self.song_length_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.main_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=10)

        # Alt Kontroller
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(pady=20)

        self.prev_button = ttk.Button(self.controls_frame, text="⏮", command=self.previous_song, width=5)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.play_button = ttk.Button(self.controls_frame, text="⏯", command=self.play_music, width=5)
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(self.controls_frame, text="⏸", command=self.pause_music, width=5)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(self.controls_frame, text="⏹", command=self.stop_music, width=5)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(self.controls_frame, text="⏭", command=self.next_song, width=5)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Ses Seviyesi
        self.volume_label = ttk.Label(self.main_frame, text="Ses Seviyesi")
        self.volume_label.pack(pady=5)

        self.volume_slider = tk.Scale(self.main_frame, from_=0, to=100, orient="horizontal", command=self.set_volume, bg=bg_color, fg=text_color, highlightbackground=bg_color, troughcolor="#1A3E3A")
        self.volume_slider.set(50)
        self.volume_slider.pack(pady=5)

        # Playlist'i Yükle
        self.load_playlist()

    # Fonksiyonlar
    def add_to_playlist(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Müzik Dosyaları", "*.mp3")])
        for file_path in file_paths:
            if file_path not in self.playlist:
                self.playlist.append(file_path)
                self.playlist_box.insert(tk.END, os.path.basename(file_path))
        self.save_playlist()

    def play_music(self):
        if self.playlist:
            pygame.mixer.music.load(self.playlist[self.current_song_index])
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.show_song_length()
            threading.Thread(target=self.update_progress).start()

    def pause_music(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.pause_button.config(text="⏸")
        else:
            pygame.mixer.music.pause()
            self.pause_button.config(text="▶")
        self.is_paused = not self.is_paused

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.song_length_label.config(text="00:00 / 00:00")
        self.progress_bar['value'] = 0

    def next_song(self):
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        self.play_music()

    def previous_song(self):
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
        self.play_music()

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val) / 100)

    def show_song_length(self):
        if self.playlist:
            song = MP3(self.playlist[self.current_song_index])
            song_length = song.info.length
            minutes, seconds = divmod(int(song_length), 60)
            self.song_length_label.config(text=f"00:00 / {minutes:02}:{seconds:02}")
            self.progress_bar['maximum'] = int(song_length)

    def update_progress(self):
        song = MP3(self.playlist[self.current_song_index])
        song_length = song.info.length
        for i in range(int(song_length)):
            if not self.is_playing or self.is_paused:
                break
            minutes, seconds = divmod(i, 60)
            self.song_length_label.config(text=f"{minutes:02}:{seconds:02} / {int(song_length) // 60:02}:{int(song_length) % 60:02}")
            self.progress_bar['value'] = i
            time.sleep(1)

    def save_playlist(self):
        with open("playlist.txt", "w") as f:
            for song in self.playlist:
                f.write(song + "\n")

    def load_playlist(self):
        if os.path.exists("playlist.txt"):
            with open("playlist.txt", "r") as f:
                for line in f:
                    song = line.strip()
                    if os.path.isfile(song):
                        self.playlist.append(song)
                        self.playlist_box.insert(tk.END, os.path.basename(song))


# Ana pencere
if __name__ == "__main__":
    root = tk.Tk()
    music_player = MusicPlayer(root)
    root.mainloop()
