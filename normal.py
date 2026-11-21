
import tkinter as tk
from tkinter import messagebox
import pygetwindow as gw
import random
import time

# ======================================
# UNIVERSAL RANDOM GAME SWITCHER
# ======================================

BG = "#171717"
PANEL = "#252525"
GREEN = "#00ff88"
WHITE = "#ffffff"

root = tk.Tk()
root.title("Universal Random Game Switcher")
root.geometry("520x650")
root.configure(bg=BG)

running = False
paused = False
remaining = 300
deadline = None
last_window = None
selected_handles = set()
window_handles = []


# ======================================
# WINDOW DETECTION
# ======================================

def refresh_windows():
    global window_handles


    # Remember currently highlighted windows
    for index in window_list.curselection():
        if index < len(window_handles):
            selected_handles.add(window_handles[index])

    window_list.delete(0, tk.END)
    window_handles = []

    try:
        windows = gw.getAllWindows()

        for window in windows:
            title = window.title.strip()

            if not title:
                continue

            if not window.visible:
                continue

            if window._hWnd == root.winfo_id():
                continue

            if "Universal Random Game Switcher" in title:
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
        messagebox.showerror("Detection Error", str(error))


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
# RANDOM SWITCHING
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
            text=f"Switched to: {chosen.title[:45]}"
        )

    except Exception as error:
        status_label.config(
            text=f"Switch failed: {error}"
        )


# ======================================
# TIMER
# ======================================

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
                interval = int(interval_entry.get())
            except ValueError:
                interval = 300

            interval = max(1, interval)

            remaining = interval
            deadline = time.monotonic() + interval

            update_display()

    root.after(100, timer_tick)


def start_timer():
    global running, paused, remaining, deadline
    global last_window

    save_selection()

    if len(selected_handles) < 2:
        messagebox.showwarning(
            "Not Enough Games",
            "Select at least 2 windows first!"
        )
        return

    try:
        interval = int(interval_entry.get())

        if interval < 1:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Invalid Interval",
            "Enter a positive number of seconds."
        )
        return

    remaining = interval
    deadline = time.monotonic() + interval

    running = True
    paused = False

    # Treat the currently focused game as
    # the previous game to avoid repeats.
    try:
        active = gw.getActiveWindow()
        last_window = active._hWnd if active else None
    except Exception:
        last_window = None

    status_label.config(text="Timer running!")
    update_display()


def pause_timer():
    global paused, deadline

    if not running:
        return

    if not paused:
        paused = True
        status_label.config(text="Timer paused")

    else:
        paused = False
        deadline = time.monotonic() + remaining
        status_label.config(text="Timer resumed")


def stop_timer():
    global running, paused, remaining, deadline

    running = False
    paused = False
    deadline = None

    try:
        remaining = max(1, int(interval_entry.get()))
    except ValueError:
        remaining = 300

    update_display()
    status_label.config(text="Timer stopped")


# ======================================
# USER INTERFACE
# ======================================

tk.Label(
    root,
    text="UNIVERSAL GAME SWITCHER",
    font=("Arial", 20, "bold"),
    fg=WHITE,
    bg=BG
).pack(pady=20)

timer_label = tk.Label(
    root,
    text="05:00",
    font=("Arial", 52, "bold"),
    fg=GREEN,
    bg=BG
)
timer_label.pack(pady=10)

tk.Label(
    root,
    text="Switch interval (seconds)",
    fg=WHITE,
    bg=BG
).pack()

interval_entry = tk.Entry(
    root,
    font=("Arial", 14),
    justify="center",
    width=12
)
interval_entry.insert(0, "300")
interval_entry.pack(pady=10)

tk.Label(
    root,
    text="SELECT WINDOWS TO SWITCH BETWEEN",
    font=("Arial", 11, "bold"),
    fg=WHITE,
    bg=BG
).pack(pady=10)

window_list = tk.Listbox(
    root,
    selectmode=tk.MULTIPLE,
    bg=PANEL,
    fg=WHITE,
    selectbackground="#008855",
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
).pack(pady=5)

tk.Button(
    root,
    text="SAVE SELECTION",
    command=save_selection,
    bg="#444444",
    fg=WHITE,
    width=20
).pack(pady=5)

controls = tk.Frame(root, bg=BG)
controls.pack(pady=15)

tk.Button(
    controls,
    text="START",
    command=start_timer,
    bg="#00cc77",
    width=10
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
    text="Ready!",
    fg=GREEN,
    bg=BG,
    wraplength=470
)
status_label.pack(pady=10)

# Initialize
refresh_windows()
timer_tick()

root.mainloop()
