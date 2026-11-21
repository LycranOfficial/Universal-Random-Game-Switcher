
import tkinter as tk
from tkinter import messagebox
import pygetwindow as gw
import random
import time

# ======================================
# GAME SWITCHER - CHAOS MODE
# ======================================

BG = "#171717"
PANEL = "#252525"
PURPLE = "#bb77ff"
WHITE = "#ffffff"

root = tk.Tk()
root.title("Game Switcher - CHAOS MODE")
root.geometry("520x680")
root.configure(bg=BG)

running = False
paused = False
remaining = 30
deadline = None
last_window = None
selected_handles = set()
window_handles = []


# ======================================
# WINDOW DETECTION
# ======================================

def refresh_windows():
    global window_handles

    for index in window_list.curselection():
        if index < len(window_handles):
            selected_handles.add(window_handles[index])

    window_list.delete(0, tk.END)
    window_handles = []

    try:
        for window in gw.getAllWindows():
            title = window.title.strip()

            if not title or not window.visible:
                continue

            if window._hWnd == root.winfo_id():
                continue

            if "Game Switcher" in title:
                continue

            window_handles.append(window._hWnd)
            window_list.insert(tk.END, title)

        for index, handle in enumerate(window_handles):
            if handle in selected_handles:
                window_list.selection_set(index)

        status_label.config(
            text=f"Found {len(window_handles)} windows"
        )

    except Exception as error:
        messagebox.showerror(
            "Detection Error", str(error)
        )


def save_selection():
    global selected_handles

    selected_handles = {
        window_handles[index]
        for index in window_list.curselection()
    }

    status_label.config(
        text=f"{len(selected_handles)} windows selected"
    )


# ======================================
# RANDOM GAME SWITCHING
# ======================================

def switch_game():
    global last_window

    available = []

    for handle in selected_handles:
        try:
            window = gw.Win32Window(handle)

            if window.title.strip():
                available.append(window)

        except Exception:
            continue

    if len(available) < 2:
        status_label.config(
            text="Need at least 2 available windows!"
        )
        return

    choices = [
        window for window in available
        if window._hWnd != last_window
    ]

    if not choices:
        choices = available

    chosen = random.choice(choices)

    try:
        if chosen.isMinimized:
            chosen.restore()

        chosen.activate()
        last_window = chosen._hWnd

        status_label.config(
            text=f"CHAOS! Switched to: {chosen.title[:40]}"
        )

    except Exception as error:
        status_label.config(
            text=f"Switch failed: {error}"
        )


# ======================================
# CHAOS TIMER
# ======================================

def get_random_interval():
    minimum = int(min_entry.get())
    maximum = int(max_entry.get())

    if minimum < 1 or maximum < minimum:
        raise ValueError

    return random.randint(minimum, maximum)


def update_display():
    minutes, seconds = divmod(max(0, remaining), 60)

    timer_label.config(
        text=f"{minutes:02}:{seconds:02}"
    )


def timer_tick():
    global remaining, deadline

    if running and not paused:
        remaining = max(
            0,
            int(deadline - time.monotonic() + 0.999)
        )

        update_display()

        if remaining == 0:
            switch_game()

            try:
                interval = get_random_interval()
            except ValueError:
                stop_timer()
                status_label.config(
                    text="Invalid Chaos interval!"
                )
                root.after(100, timer_tick)
                return

            remaining = interval
            deadline = time.monotonic() + interval
            update_display()

    root.after(100, timer_tick)


def start_timer():
    global running, paused, remaining
    global deadline, last_window

    save_selection()

    if len(selected_handles) < 2:
        messagebox.showwarning(
            "Not Enough Windows",
            "Select at least 2 windows first!"
        )
        return

    try:
        interval = get_random_interval()
    except ValueError:
        messagebox.showerror(
            "Invalid Interval",
            "Enter valid minimum and maximum seconds."
        )
        return

    remaining = interval
    deadline = time.monotonic() + interval

    running = True
    paused = False

    try:
        active = gw.getActiveWindow()
        last_window = active._hWnd if active else None
    except Exception:
        last_window = None

    update_display()
    status_label.config(
        text=f"CHAOS ACTIVE! Next switch in {interval}s"
    )


def pause_timer():
    global paused, deadline

    if not running:
        return

    if not paused:
        paused = True
        status_label.config(text="CHAOS PAUSED")
    else:
        paused = False
        deadline = time.monotonic() + remaining
        status_label.config(text="CHAOS RESUMED")


def stop_timer():
    global running, paused, remaining, deadline

    running = False
    paused = False
    deadline = None
    remaining = 0

    update_display()
    status_label.config(text="CHAOS STOPPED")


# ======================================
# USER INTERFACE
# ======================================

tk.Label(
    root,
    text="GAME SWITCHER - CHAOS MODE",
    font=("Arial", 19, "bold"),
    fg=PURPLE,
    bg=BG
).pack(pady=15)

timer_label = tk.Label(
    root,
    text="00:30",
    font=("Arial", 52, "bold"),
    fg=PURPLE,
    bg=BG
)
timer_label.pack(pady=10)

tk.Label(
    root,
    text="RANDOM SWITCH INTERVAL",
    font=("Arial", 11, "bold"),
    fg=WHITE,
    bg=BG
).pack(pady=5)

settings = tk.Frame(root, bg=BG)
settings.pack(pady=5)

tk.Label(
    settings,
    text="Minimum (seconds)",
    fg=WHITE,
    bg=BG
).grid(row=0, column=0, padx=15)

tk.Label(
    settings,
    text="Maximum (seconds)",
    fg=WHITE,
    bg=BG
).grid(row=0, column=1, padx=15)

min_entry = tk.Entry(
    settings,
    width=12,
    justify="center",
    font=("Arial", 13)
)
min_entry.insert(0, "30")
min_entry.grid(row=1, column=0, pady=5)

max_entry = tk.Entry(
    settings,
    width=12,
    justify="center",
    font=("Arial", 13)
)
max_entry.insert(0, "300")
max_entry.grid(row=1, column=1, pady=5)

tk.Label(
    root,
    text="SELECT WINDOWS",
    font=("Arial", 11, "bold"),
    fg=WHITE,
    bg=BG
).pack(pady=10)

window_list = tk.Listbox(
    root,
    selectmode=tk.MULTIPLE,
    bg=PANEL,
    fg=WHITE,
    selectbackground="#7733aa",
    width=60,
    height=10,
    exportselection=False
)
window_list.pack(padx=15, pady=5)

tk.Button(
    root,
    text="REFRESH WINDOWS",
    command=refresh_windows,
    bg="#444444",
    fg=WHITE,
    width=20
).pack(pady=4)

tk.Button(
    root,
    text="SAVE SELECTION",
    command=save_selection,
    bg="#444444",
    fg=WHITE,
    width=20
).pack(pady=4)

controls = tk.Frame(root, bg=BG)
controls.pack(pady=15)

tk.Button(
    controls,
    text="START CHAOS",
    command=start_timer,
    bg=PURPLE,
    width=13
).grid(row=0, column=0, padx=5)

tk.Button(
    controls,
    text="PAUSE / RESUME",
    command=pause_timer,
    bg="#ffaa00",
    width=15
).grid(row=0, column=1, padx=5)

tk.Button(
    controls,
    text="STOP",
    command=stop_timer,
    bg="#ff4444",
    fg=WHITE,
    width=10
).grid(row=0, column=2, padx=5)

status_label = tk.Label(
    root,
    text="CHAOS MODE READY",
    fg=PURPLE,
    bg=BG,
    wraplength=470
)
status_label.pack(pady=10)

# Start application
refresh_windows()
timer_tick()

root.mainloop()
