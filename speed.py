
import tkinter as tk
from tkinter import messagebox
import pygetwindow as gw
import random
import time
import math

# ==========================================
# GAME SWITCHER - SPEED ESCALATION MODE
# ==========================================

BG = "#171717"
PANEL = "#252525"
ORANGE = "#ff9933"
WHITE = "#ffffff"

root = tk.Tk()
root.title("Game Switcher - SPEED MODE")
root.geometry("540x720")
root.configure(bg=BG)

running = False
paused = False
remaining = 60
deadline = None
current_interval = 60
decrease_amount = 10
minimum_interval = 5
switch_count = 0
last_window = None

selected_handles = set()
window_handles = []


# ==========================================
# WINDOW DETECTION
# ==========================================

def refresh_windows():
    global window_handles

    # Preserve highlighted selections
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


# ==========================================
# RANDOM WINDOW SWITCHING
# ==========================================

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
        return False

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
            text=f"Switched to: {chosen.title[:45]}"
        )
        return True

    except Exception as error:
        status_label.config(
            text=f"Switch failed: {error}"
        )
        return False


# ==========================================
# SPEED ESCALATION TIMER
# ==========================================

def update_display():
    minutes, seconds = divmod(
        max(0, remaining), 60
    )

    timer_label.config(
        text=f"{minutes:02}:{seconds:02}"
    )

    interval_label.config(
        text=f"Current interval: {current_interval}s"
    )

    switch_label.config(
        text=f"Successful switches: {switch_count}"
    )


def timer_tick():
    global remaining, deadline
    global current_interval, switch_count

    if running and not paused:
        remaining = max(
            0,
            math.ceil(deadline - time.monotonic())
        )

        update_display()

        if remaining == 0:
            success = switch_game()

            if success:
                switch_count += 1

                current_interval = max(
                    minimum_interval,
                    current_interval - decrease_amount
                )

            remaining = current_interval
            deadline = time.monotonic() + remaining

            update_display()

    root.after(100, timer_tick)


def start_timer():
    global running, paused, remaining
    global deadline, current_interval
    global decrease_amount, minimum_interval
    global switch_count, last_window

    save_selection()

    if len(selected_handles) < 2:
        messagebox.showwarning(
            "Not Enough Windows",
            "Select at least 2 windows first!"
        )
        return

    try:
        start = int(start_entry.get())
        decrease = int(decrease_entry.get())
        minimum = int(min_entry.get())

        if (
            start < 1
            or decrease < 1
            or minimum < 1
            or minimum > start
        ):
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Invalid Settings",
            "Enter positive numbers. Minimum "
            "must not exceed starting interval."
        )
        return

    current_interval = start
    decrease_amount = decrease
    minimum_interval = minimum
    switch_count = 0

    remaining = current_interval
    deadline = time.monotonic() + remaining

    running = True
    paused = False

    try:
        active = gw.getActiveWindow()
        last_window = active._hWnd if active else None
    except Exception:
        last_window = None

    status_label.config(text="SPEED MODE ACTIVE!")
    update_display()


def pause_timer():
    global paused, deadline, remaining

    if not running:
        return

    if not paused:
        remaining = max(
            0,
            math.ceil(deadline - time.monotonic())
        )
        paused = True
        status_label.config(text="SPEED MODE PAUSED")

    else:
        paused = False
        deadline = time.monotonic() + remaining
        status_label.config(text="SPEED MODE RESUMED")

    update_display()


def stop_timer():
    global running, paused, remaining
    global deadline, current_interval, switch_count

    running = False
    paused = False
    deadline = None
    remaining = 0
    switch_count = 0

    update_display()
    status_label.config(text="SPEED MODE STOPPED")


# ==========================================
# USER INTERFACE
# ==========================================

tk.Label(
    root,
    text="GAME SWITCHER - SPEED MODE",
    font=("Arial", 19, "bold"),
    fg=ORANGE,
    bg=BG
).pack(pady=15)

timer_label = tk.Label(
    root,
    text="01:00",
    font=("Arial", 52, "bold"),
    fg=ORANGE,
    bg=BG
)
timer_label.pack(pady=8)

interval_label = tk.Label(
    root,
    text="Current interval: 60s",
    font=("Arial", 11),
    fg=WHITE,
    bg=BG
)
interval_label.pack(pady=3)

switch_label = tk.Label(
    root,
    text="Successful switches: 0",
    font=("Arial", 11),
    fg=WHITE,
    bg=BG
)
switch_label.pack(pady=3)

tk.Label(
    root,
    text="SPEED ESCALATION SETTINGS",
    font=("Arial", 11, "bold"),
    fg=WHITE,
    bg=BG
).pack(pady=12)

settings = tk.Frame(root, bg=BG)
settings.pack(pady=5)

def add_setting(column, label, default):
    tk.Label(
        settings,
        text=label,
        fg=WHITE,
        bg=BG
    ).grid(row=0, column=column, padx=8)

    entry = tk.Entry(
        settings,
        width=11,
        justify="center",
        font=("Arial", 12)
    )
    entry.insert(0, str(default))
    entry.grid(row=1, column=column, pady=5)

    return entry


start_entry = add_setting(
    0, "Start (seconds)", 60
)

decrease_entry = add_setting(
    1, "Decrease (seconds)", 10
)

min_entry = add_setting(
    2, "Minimum (seconds)", 5
)

tk.Label(
    root,
    text="SELECT WINDOWS",
    font=("Arial", 11, "bold"),
    fg=WHITE,
    bg=BG
).pack(pady=12)

window_list = tk.Listbox(
    root,
    selectmode=tk.MULTIPLE,
    bg=PANEL,
    fg=WHITE,
    selectbackground="#aa6611",
    width=65,
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
    text="START SPEED",
    command=start_timer,
    bg=ORANGE,
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
    text="SPEED MODE READY",
    fg=ORANGE,
    bg=BG,
    wraplength=490
)
status_label.pack(pady=10)

# Initialize
refresh_windows()
timer_tick()

root.mainloop()
