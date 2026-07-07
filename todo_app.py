"""
To-Do List — a simple desktop task manager built with Tkinter.

Features:
    - Add tasks
    - View all tasks
    - Mark tasks complete / incomplete
    - Delete tasks
    - Tasks persist between sessions in a local JSON file (tasks.json)

Run with:
    python3 todo_app.py

No third-party packages required — everything here is Python's standard library.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ----------------------------------------------------------------------
# Config / constants
# ----------------------------------------------------------------------

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "tasks.json")

BG = "#F6F7F5"          # app background
CARD = "#FFFFFF"        # row / card background
BORDER = "#E3E5E0"      # subtle borders
TEXT_MAIN = "#1F2A24"   # primary text
TEXT_MUTED = "#7C877F"  # secondary text
ACCENT = "#2F6F5E"      # primary buttons / focus (deep teal-green)
ACCENT_HOVER = "#25594B"
DANGER = "#C2513F"      # delete
DANGER_HOVER = "#A43F30"

FONT_FAMILY = "Segoe UI"  # Tk gracefully substitutes if unavailable on the OS


# ----------------------------------------------------------------------
# Data layer
# ----------------------------------------------------------------------

class TaskStore:
    """Handles loading and saving tasks to a JSON file on disk."""

    def __init__(self, path):
        self.path = path
        self.tasks = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable file — start fresh rather than crash.
            return []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def add(self, text):
        new_id = (max((t["id"] for t in self.tasks), default=0)) + 1
        self.tasks.append({
            "id": new_id,
            "text": text,
            "done": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        self.save()

    def toggle_done(self, task_id):
        for t in self.tasks:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                break
        self.save()

    def delete(self, task_id):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.save()


# ----------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------

class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("480x600")
        self.minsize(380, 420)
        self.configure(bg=BG)

        self.store = TaskStore(DATA_FILE)

        self._build_style()
        self._build_header()
        self._build_input_row()
        self._build_task_list()
        self._build_footer()

        self.refresh()

    # ---- style -----------------------------------------------------

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="white",
            font=(FONT_FAMILY, 10, "bold"),
            padding=(14, 8),
            borderwidth=0,
        )
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])

        style.configure(
            "TCheckbutton",
            background=CARD,
            font=(FONT_FAMILY, 11),
        )

    # ---- header ------------------------------------------------------

    def _build_header(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(24, 8))

        tk.Label(
            header, text="My Tasks", bg=BG, fg=TEXT_MAIN,
            font=(FONT_FAMILY, 22, "bold"),
        ).pack(anchor="w")

        self.subtitle_var = tk.StringVar()
        tk.Label(
            header, textvariable=self.subtitle_var, bg=BG, fg=TEXT_MUTED,
            font=(FONT_FAMILY, 10),
        ).pack(anchor="w", pady=(2, 0))

    # ---- input row ---------------------------------------------------

    def _build_input_row(self):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=24, pady=(8, 12))

        self.entry_var = tk.StringVar()
        entry = tk.Entry(
            row, textvariable=self.entry_var, font=(FONT_FAMILY, 12),
            relief="flat", bg=CARD, fg=TEXT_MAIN,
            insertbackground=TEXT_MAIN, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT,
        )
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        entry.bind("<Return>", lambda e: self.add_task())
        entry.focus_set()

        add_btn = ttk.Button(
            row, text="+ Add", style="Accent.TButton", command=self.add_task,
        )
        add_btn.pack(side="left")

    # ---- task list -----------------------------------------------------

    def _build_task_list(self):
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=BG)

        self.list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)   # Windows / macOS
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ---- footer ---------------------------------------------------------

    def _build_footer(self):
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=24, pady=(0, 16))
        self.footer_var = tk.StringVar()
        tk.Label(
            footer, textvariable=self.footer_var, bg=BG, fg=TEXT_MUTED,
            font=(FONT_FAMILY, 9),
        ).pack(anchor="w")

    # ---- actions ----------------------------------------------------------

    def add_task(self):
        text = self.entry_var.get().strip()
        if not text:
            return
        self.store.add(text)
        self.entry_var.set("")
        self.refresh()

    def toggle_task(self, task_id):
        self.store.toggle_done(task_id)
        self.refresh()

    def delete_task(self, task_id, text):
        if messagebox.askyesno("Delete task", f'Delete "{text}"?'):
            self.store.delete(task_id)
            self.refresh()

    # ---- rendering ----------------------------------------------------------

    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        tasks = self.store.tasks
        if not tasks:
            empty = tk.Label(
                self.list_frame,
                text="No tasks yet — add your first one above.",
                bg=BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 11),
            )
            empty.pack(pady=40)
        else:
            # Incomplete tasks first, then completed; newest first within each group.
            ordered = sorted(tasks, key=lambda t: (t["done"], -t["id"]))
            for task in ordered:
                self._render_task_row(task)

        total = len(tasks)
        done = sum(1 for t in tasks if t["done"])
        remaining = total - done
        if total == 0:
            self.subtitle_var.set("Nothing on your list right now")
        else:
            self.subtitle_var.set(f"{remaining} remaining · {done} completed")
        self.footer_var.set(f"Saved locally to {os.path.basename(DATA_FILE)}")

    def _render_task_row(self, task):
        row = tk.Frame(self.list_frame, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1)
        row.pack(fill="x", pady=4)

        done_var = tk.BooleanVar(value=task["done"])
        chk = ttk.Checkbutton(
            row, variable=done_var,
            command=lambda: self.toggle_task(task["id"]),
        )
        chk.pack(side="left", padx=(12, 4), pady=10)

        label_font = (FONT_FAMILY, 11, "overstrike") if task["done"] else (FONT_FAMILY, 11)
        label_fg = TEXT_MUTED if task["done"] else TEXT_MAIN
        label = tk.Label(
            row, text=task["text"], bg=CARD, fg=label_fg, font=label_font,
            anchor="w", justify="left", wraplength=300,
        )
        label.pack(side="left", fill="x", expand=True, pady=10)

        del_btn = tk.Label(
            row, text="✕", bg=CARD, fg=DANGER, font=(FONT_FAMILY, 11, "bold"),
            cursor="hand2",
        )
        del_btn.pack(side="right", padx=12)
        del_btn.bind("<Button-1>", lambda e: self.delete_task(task["id"], task["text"]))
        del_btn.bind("<Enter>", lambda e: del_btn.configure(fg=DANGER_HOVER))
        del_btn.bind("<Leave>", lambda e: del_btn.configure(fg=DANGER))


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
