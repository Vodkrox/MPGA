import subprocess
import tkinter as tk
from tkinter import messagebox, font
from urllib.parse import urlparse, parse_qs
import random

BACKGROUND_COLOR = "#A0BCE6"
BACKGROUND_COLOR_SEMI = "#A0BCE6"
BUTTON_COLOR = "#4CAF50"
BUTTON_HOVER_COLOR = "#388E3C"
TEXT_COLOR = "#1C1C1C"
STATUS_OK_COLOR = "#2E7D32"
STATUS_ERROR_COLOR = "#D32F2F"

DROPS_COUNT = 30
DROP_COLOR = "#74b9ff"
DROP_RADIUS_MIN = 4
DROP_RADIUS_MAX = 8
DROP_SPEED_MIN = 1
DROP_SPEED_MAX = 3
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 180

class Drop:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(-WINDOW_HEIGHT, 0)
        self.radius = random.randint(DROP_RADIUS_MIN, DROP_RADIUS_MAX)
        self.speed = random.uniform(DROP_SPEED_MIN, DROP_SPEED_MAX)
        self.id = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=DROP_COLOR, outline="", stipple='gray25'
        )

    def move(self):
        self.y += self.speed
        if self.y - self.radius > WINDOW_HEIGHT:
            self.x = random.randint(0, WINDOW_WIDTH)
            self.y = random.randint(-WINDOW_HEIGHT, 0)
            self.radius = random.randint(DROP_RADIUS_MIN, DROP_RADIUS_MAX)
            self.speed = random.uniform(DROP_SPEED_MIN, DROP_SPEED_MAX)
        self.canvas.coords(
            self.id,
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )

def clean_youtube_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    video_id = query.get("v")
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id[0]}"
    else:
        return url

def get_audio_url_yt_dlp(user_url):
    clean_url = clean_youtube_url(user_url)
    try:
        result = subprocess.run(
            ['yt-dlp', '-f', 'bestaudio[abr>=128]', '-g', clean_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        )
        audio_url = result.stdout.strip()
        return audio_url
    except subprocess.CalledProcessError:
        return None

def open_in_wmp(url):
    wmp_paths = [
        r"C:\Program Files\Windows Media Player\wmplayer.exe",
        r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"
    ]
    for path in wmp_paths:
        try:
            subprocess.Popen([path, url])
            return True
        except FileNotFoundError:
            continue
    return False

def clear_status():
    lbl_status.config(text="")

def play_audio():
    user_url = entry_url.get()
    if not user_url.strip():
        messagebox.showwarning("Warning", "Please enter a YouTube URL.")
        return
    audio_url = get_audio_url_yt_dlp(user_url)
    if audio_url:
        lbl_status.config(text="Loading, plz be patient :3", fg=STATUS_OK_COLOR)
        success = open_in_wmp(audio_url)
        if not success:
            lbl_status.config(text="Windows Media Player not found.", fg=STATUS_ERROR_COLOR)
    else:
        lbl_status.config(text="Error getting audio URL. Check the URL and yt-dlp.", fg=STATUS_ERROR_COLOR)
    
    root.after(7000, clear_status)

def on_enter(event):
    btn_canvas.itemconfig(btn_rect, fill=BUTTON_HOVER_COLOR)

def on_leave(event):
    btn_canvas.itemconfig(btn_rect, fill=BUTTON_COLOR)

def on_click(event):
    play_audio()

def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1+radius, y1,
        x1+radius, y1,
        x2-radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

root = tk.Tk()
root.title("MPGA (by Pedritochi ^_^)")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.attributes("-alpha", 0.95)

label_font = font.Font(family="Segoe UI", size=11)
entry_font = font.Font(family="Segoe UI", size=10)
button_font = font.Font(family="Segoe UI Semibold", size=11)

canvas_bg = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
canvas_bg.place(x=0, y=0)

round_rectangle(canvas_bg, 5, 5, WINDOW_WIDTH-5, WINDOW_HEIGHT-5, radius=20, fill=BACKGROUND_COLOR_SEMI)

lbl_instruc = tk.Label(root, text="Enter YouTube video URL:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=label_font)
lbl_instruc.place(x=25, y=20)

frame_entry = tk.Frame(root, bg="white", bd=0)
frame_entry.place(x=25, y=50, width=430, height=28)
entry_url = tk.Entry(frame_entry, font=entry_font, bd=0, relief="flat")
entry_url.pack(fill="both", padx=8, pady=2)

btn_canvas = tk.Canvas(root, width=220, height=40, highlightthickness=0, bg=BACKGROUND_COLOR)
btn_canvas.place(x=130, y=95)
btn_rect = round_rectangle(btn_canvas, 0, 0, 220, 40, radius=20, fill=BUTTON_COLOR)
btn_text = btn_canvas.create_text(110, 20, text="Play on Windows Media Player", fill="white", font=button_font)

btn_canvas.bind("<Enter>", on_enter)
btn_canvas.bind("<Leave>", on_leave)
btn_canvas.bind("<Button-1>", on_click)

lbl_status = tk.Label(root, text="", bg=BACKGROUND_COLOR, fg=STATUS_OK_COLOR, font=label_font)
lbl_status.place(x=25, y=145)

drops = [Drop(canvas_bg) for _ in range(DROPS_COUNT)]

def animate_drops():
    for drop in drops:
        drop.move()
    root.after(50, animate_drops)

animate_drops()

root.mainloop()


