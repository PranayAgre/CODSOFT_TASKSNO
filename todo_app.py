"""
Simple desktop to-do list app built with Tkinter.

Tasks are saved to tasks.json next to this script, so your list is
still there the next time you open it. No external dependencies —
just the Python standard library.

Run:
    python3 todo_app.py
"""

import json
import os
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "tasks.json")

# colors — deep teal/green, kept it simple
BG = "#F6F7F5"
CARD = "#FFFFFF"
BORDER = "#E3E5E0"
TEXT_MAIN = "#1F2A24"
TEXT_MUTED = "#7C877F"
ACCENT = "#2F6F5E"
ACCENT_HOVER = "#25594B"
DANGER = "#C2513F"
DANGER_HOVER = "#A43F30"

FONT = "Segoe UI"  # Tk falls back to a sane default on Linux/macOS


class TaskStore:
    """Reads/writes tasks.json and keeps the in-memory task list in sync."""

    def __init__(self, path):
        self.path = path
        self.tasks = self._load()
        # keep a running counter instead of rescanning the list for max(id)
        # on every add — same uniqueness guarantee, just O(1) instead of O(n)
        self._next_id = max((t["id"] for t in self.tasks), default=0) + 1

    def _load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            # file got corrupted somehow — don't crash, just start fresh
            return []

    def save(self):
        # write to a temp file and swap it in, so a crash mid-write can't
        # leave tasks.json half-written / corrupted
        tmp_fd, tmp_path = tempfile.mkstemp(dir=APP_DIR, suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.path)
        except OSError:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def add(self, text):
        self.tasks.append({
            "id": self._next_id,
            "text": text,
            "done": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        self._next_id += 1
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


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("480x600")
        self.minsize(380, 420)
        self.configure(bg=BG)

        self.store = TaskStore(DATA_FILE)
        self._labels = []      # task labels on screen right now, for resize handling
        self._resize_job = None

        self._build_style()
        self._build_header()
        self._build_input_row()
        self._build_task_list()
        self._build_footer()

        self.bind("<Configure>", self._on_window_resize)
        self.refresh()

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Accent.TButton", background=ACCENT, foreground="white",
                         font=(FONT, 10, "bold"), padding=(14, 8), borderwidth=0)
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])
        style.configure("TCheckbutton", background=CARD, font=(FONT, 11))

    def _build_header(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(24, 8))

        tk.Label(header, text="My Tasks", bg=BG, fg=TEXT_MAIN,
                 font=(FONT, 22, "bold")).pack(anchor="w")

        self.subtitle_var = tk.StringVar()
        tk.Label(header, textvariable=self.subtitle_var, bg=BG, fg=TEXT_MUTED,
                 font=(FONT, 10)).pack(anchor="w", pady=(2, 0))

    def _build_input_row(self):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=24, pady=(8, 12))

        self.entry_var = tk.StringVar()
        entry = tk.Entry(row, textvariable=self.entry_var, font=(FONT, 12),
                          relief="flat", bg=CARD, fg=TEXT_MAIN,
                          insertbackground=TEXT_MAIN, highlightthickness=1,
                          highlightbackground=BORDER, highlightcolor=ACCENT)
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        entry.bind("<Return>", lambda e: self.add_task())
        entry.focus_set()

        ttk.Button(row, text="+ Add", style="Accent.TButton",
                   command=self.add_task).pack(side="left")

    def _build_task_list(self):
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg=BG)

        self.list_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)          # Windows / macOS
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_mousewheel(self, event):
        # macOS reports small raw delta values (±1, ±2...), Windows/Linux
        # report multiples of 120 — dividing mac's delta by 120 would just
        # round to zero and scrolling would silently do nothing
        if sys.platform == "darwin":
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_footer(self):
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=24, pady=(0, 16))
        self.footer_var = tk.StringVar()
        tk.Label(footer, textvariable=self.footer_var, bg=BG, fg=TEXT_MUTED,
                 font=(FONT, 9)).pack(anchor="w")

    # -- actions --

    def add_task(self):
        text = self.entry_var.get().strip()
        if not text:
            return
        if not self._try(self.store.add, text):
            return
        self.entry_var.set("")
        self.refresh()

    def toggle_task(self, task_id):
        if self._try(self.store.toggle_done, task_id):
            self.refresh()

    def delete_task(self, task_id, text):
        if not messagebox.askyesno("Delete task", f'Delete "{text}"?'):
            return
        if self._try(self.store.delete, task_id):
            self.refresh()

    def _try(self, fn, *args):
        """Run a store operation and surface disk errors instead of crashing."""
        try:
            fn(*args)
            return True
        except OSError as e:
            messagebox.showerror("Couldn't save", f"Your change wasn't saved:\n{e}")
            return False

    # -- rendering --

    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        self._labels.clear()

        tasks = self.store.tasks
        if not tasks:
            tk.Label(self.list_frame, text="No tasks yet — add your first one above.",
                     bg=BG, fg=TEXT_MUTED, font=(FONT, 11)).pack(pady=40)
        else:
            # unfinished tasks on top, newest first within each group
            for task in sorted(tasks, key=lambda t: (t["done"], -t["id"])):
                self._render_task_row(task)

        total = len(tasks)
        done = sum(1 for t in tasks if t["done"])
        if total == 0:
            self.subtitle_var.set("Nothing on your list right now")
        else:
            self.subtitle_var.set(f"{total - done} remaining · {done} completed")
        self.footer_var.set(f"Saved locally to {os.path.basename(DATA_FILE)}")

    def _render_task_row(self, task):
        row = tk.Frame(self.list_frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", pady=4)

        done_var = tk.BooleanVar(value=task["done"])
        ttk.Checkbutton(row, variable=done_var,
                        command=lambda: self.toggle_task(task["id"])
                        ).pack(side="left", padx=(12, 4), pady=10)

        label_font = (FONT, 11, "overstrike") if task["done"] else (FONT, 11)
        label = tk.Label(row, text=task["text"], bg=CARD,
                          fg=TEXT_MUTED if task["done"] else TEXT_MAIN,
                          font=label_font, anchor="w", justify="left",
                          wraplength=self._wraplength())
        label.pack(side="left", fill="x", expand=True, pady=10)
        self._labels.append(label)

        del_btn = tk.Label(row, text="✕", bg=CARD, fg=DANGER, font=(FONT, 11, "bold"), cursor="hand2")
        del_btn.pack(side="right", padx=12)
        del_btn.bind("<Button-1>", lambda e: self.delete_task(task["id"], task["text"]))
        del_btn.bind("<Enter>", lambda e: del_btn.configure(fg=DANGER_HOVER))
        del_btn.bind("<Leave>", lambda e: del_btn.configure(fg=DANGER))

    def _wraplength(self):
        # leaves room for the checkbox, delete button and padding
        width = self.winfo_width()
        if width <= 1:
            width = 480  # window isn't mapped yet, fall back to the initial size
        return max(180, width - 140)

    def _on_window_resize(self, event):
        # re-wrap task text after a resize, but debounced — otherwise dragging
        # the window edge would re-layout every row on every pixel of movement
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(150, self._update_wraplengths)

    def _update_wraplengths(self):
        self._resize_job = None
        wrap = self._wraplength()
        for label in self._labels:
            label.configure(wraplength=wrap)


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
