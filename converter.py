"""
Font Converter — WOFF2 ↔ TTF
- Paste a path or drag & drop a folder
- Choose direction: WOFF2→TTF or TTF→WOFF2
- Click Convert, then Save to pick output location
"""

import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _HAS_DND = True
except Exception:
    _HAS_DND = False


def _resource(rel: str) -> str:
    """Resolve a bundled resource path — works both live and in a PyInstaller exe."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel)


# ── Theme — black / white / #F67D31 ───────────────────────────────────────
BG       = "#0d0d0d"   # near-black background
SURFACE  = "#1a1a1a"   # card / zone background
SURFACE2 = "#242424"   # input / secondary surface
ACCENT   = "#F67D31"   # orange
ACCENT_H = "#ff9550"   # orange hover
ACCENT_D = "#c45e1a"   # orange pressed
TEXT     = "#ffffff"   # white
MUTED    = "#666666"   # grey labels
SUCCESS  = "#F67D31"   # use accent for success (on-brand)
ERROR    = "#ff4d4d"   # red errors
BORDER   = "#2e2e2e"   # subtle border

WIN_W, WIN_H = 540, 460


# ── Conversion ─────────────────────────────────────────────────────────────
def _get_files(folder: Path, direction: str):
    ext = "*.woff2" if direction == "woff2_to_ttf" else "*.ttf"
    return sorted(folder.rglob(ext))

def _convert(src: Path, dst: Path, direction: str):
    from fontTools.ttLib import TTFont
    font = TTFont(str(src))
    font.flavor = None if direction == "woff2_to_ttf" else "woff2"
    font.save(str(dst))

def _run_conversion(folder: Path, out_dir: Path, direction: str,
                    on_progress, on_done):
    files = _get_files(folder, direction)
    if not files:
        on_done([], [], out_dir)
        return

    out_ext   = ".ttf" if direction == "woff2_to_ttf" else ".woff2"
    converted = []
    errors    = []

    for i, src in enumerate(files, 1):
        dst = out_dir / (src.stem + out_ext)
        try:
            _convert(src, dst, direction)
            converted.append(dst)
        except Exception as exc:
            errors.append(f"{src.name}: {exc}")
        on_progress(i, len(files))

    on_done(converted, errors, out_dir)


# ── App ────────────────────────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root = root
        root.title("Font Converter")
        root.geometry(f"{WIN_W}x{WIN_H}")
        root.resizable(False, False)
        root.configure(bg=BG)

        # Window icon
        try:
            root.iconbitmap(_resource("icon.ico"))
        except Exception:
            pass

        self._converted_files = []
        self._temp_out_dir    = None
        self._source_folder   = None

        self._build_ui()

    def _build_ui(self):
        r = self.root

        # ── Header ──────────────────────────────────────────────────────
        hdr = tk.Frame(r, bg=BG)
        hdr.pack(fill="x", padx=32, pady=(24, 0))

        # Icon + title on same row
        title_row = tk.Frame(hdr, bg=BG)
        title_row.pack(anchor="w")

        tk.Label(title_row, text="Font Converter",
                 font=("Segoe UI", 20, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")

        # Orange accent dot after title
        tk.Label(title_row, text=".", font=("Segoe UI", 24, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left", pady=(0, 4))

        tk.Label(hdr, text="WOFF2  ↔  TTF  |  paste a path or drag & drop",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))

        # Orange rule under header
        tk.Frame(r, bg=ACCENT, height=2).pack(fill="x", padx=32, pady=(10, 0))

        # ── Direction toggle ─────────────────────────────────────────────
        tog = tk.Frame(r, bg=BG)
        tog.pack(fill="x", padx=32, pady=(14, 0))

        tk.Label(tog, text="DIRECTION", font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 6))

        btn_row = tk.Frame(tog, bg=BG)
        btn_row.pack(anchor="w")

        self._direction = tk.StringVar(value="woff2_to_ttf")

        self._btn_a = tk.Button(btn_row, text="WOFF2  →  TTF",
                                font=("Segoe UI", 10, "bold"),
                                relief="flat", bd=0, padx=16, pady=7,
                                cursor="hand2",
                                command=lambda: self._set_dir("woff2_to_ttf"))
        self._btn_a.pack(side="left", padx=(0, 6))

        self._btn_b = tk.Button(btn_row, text="TTF  →  WOFF2",
                                font=("Segoe UI", 10, "bold"),
                                relief="flat", bd=0, padx=16, pady=7,
                                cursor="hand2",
                                command=lambda: self._set_dir("ttf_to_woff2"))
        self._btn_b.pack(side="left")

        # ── Drop / paste zone ────────────────────────────────────────────
        zone_wrap = tk.Frame(r, bg=BG)
        zone_wrap.pack(fill="x", padx=32, pady=(16, 0))

        tk.Label(zone_wrap, text="SOURCE FOLDER", font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 6))

        self.drop_frame = tk.Frame(zone_wrap, bg=SURFACE,
                                   highlightthickness=1,
                                   highlightbackground=BORDER,
                                   highlightcolor=ACCENT)
        self.drop_frame.pack(fill="x")

        # Top half
        drop_top = tk.Frame(self.drop_frame, bg=SURFACE, height=72)
        drop_top.pack(fill="x")
        drop_top.pack_propagate(False)

        self.drop_icon = tk.Label(drop_top, text="📂",
                                  font=("Segoe UI Emoji", 20),
                                  bg=SURFACE, fg=ACCENT)
        self.drop_icon.pack(side="left", padx=(16, 8))

        drop_text = tk.Frame(drop_top, bg=SURFACE)
        drop_text.pack(side="left", fill="both", expand=True)

        self.drop_title = tk.Label(drop_text, text="Drop folder here",
                                   font=("Segoe UI", 11, "bold"),
                                   bg=SURFACE, fg=TEXT, anchor="w")
        self.drop_title.pack(anchor="w", pady=(16, 0))

        self.drop_sub = tk.Label(drop_text,
                                 text="or paste path below / click Browse",
                                 font=("Segoe UI", 9), bg=SURFACE,
                                 fg=MUTED, anchor="w")
        self.drop_sub.pack(anchor="w")

        browse_btn = tk.Button(drop_top, text="Browse",
                               font=("Segoe UI", 9, "bold"),
                               bg=ACCENT, fg="#fff",
                               activebackground=ACCENT_H,
                               activeforeground="#fff",
                               relief="flat", bd=0, padx=14, pady=6,
                               cursor="hand2", command=self._browse)
        browse_btn.pack(side="right", padx=14)

        # Divider
        tk.Frame(self.drop_frame, bg=BORDER, height=1).pack(fill="x")

        # Path input row
        path_row = tk.Frame(self.drop_frame, bg=SURFACE, pady=8)
        path_row.pack(fill="x", padx=12)

        self.path_var = tk.StringVar()
        self.path_var.trace_add("write", self._on_path_typed)

        self.path_entry = tk.Entry(path_row, textvariable=self.path_var,
                                   font=("Consolas", 9), bg=SURFACE2,
                                   fg=TEXT, insertbackground=ACCENT,
                                   relief="flat", bd=0,
                                   highlightthickness=0)
        self.path_entry.pack(fill="x", ipady=7, padx=4)

        # DnD
        if _HAS_DND:
            for w in (self.drop_frame, drop_top, drop_text,
                      self.drop_icon, self.drop_title, self.drop_sub):
                w.drop_target_register(DND_FILES)
                w.dnd_bind("<<Drop>>", self._on_drop)

        # ── Action buttons ───────────────────────────────────────────────
        act = tk.Frame(r, bg=BG)
        act.pack(fill="x", padx=32, pady=(16, 0))

        self.convert_btn = tk.Button(act, text="Convert",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=ACCENT, fg="#fff",
                                     activebackground=ACCENT_H,
                                     activeforeground="#fff",
                                     relief="flat", bd=0,
                                     padx=28, pady=10,
                                     cursor="hand2",
                                     command=self._on_convert)
        self.convert_btn.pack(side="left", padx=(0, 10))

        self.save_btn = tk.Button(act, text="Save to…",
                                  font=("Segoe UI", 11),
                                  bg=SURFACE2, fg=MUTED,
                                  activebackground=ACCENT,
                                  activeforeground="#fff",
                                  relief="flat", bd=0,
                                  padx=28, pady=10,
                                  cursor="hand2",
                                  state="disabled",
                                  command=self._on_save)
        self.save_btn.pack(side="left")

        # ── Progress bar ─────────────────────────────────────────────────
        prog_wrap = tk.Frame(r, bg=BG)
        prog_wrap.pack(fill="x", padx=32, pady=(14, 0))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("C.Horizontal.TProgressbar",
                        troughcolor=SURFACE2, background=ACCENT,
                        thickness=4, borderwidth=0)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(prog_wrap,
                                            variable=self.progress_var,
                                            maximum=100, length=WIN_W - 64,
                                            mode="determinate",
                                            style="C.Horizontal.TProgressbar")
        self.progress_bar.pack()

        # ── Status label ─────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(r, textvariable=self.status_var,
                                   font=("Segoe UI", 9), bg=BG, fg=MUTED,
                                   wraplength=WIN_W - 64, justify="left")
        self.status_lbl.pack(anchor="w", padx=32, pady=(8, 0))

        # Apply initial toggle style now that all widgets exist
        self._set_dir("woff2_to_ttf")

    # ── Direction toggle ───────────────────────────────────────────────────
    def _set_dir(self, val: str):
        self._direction.set(val)
        on  = dict(bg=ACCENT,   fg="#fff",  activebackground=ACCENT_H)
        off = dict(bg=SURFACE2, fg=MUTED,   activebackground=SURFACE2)
        if val == "woff2_to_ttf":
            self._btn_a.configure(**on)
            self._btn_b.configure(**off)
        else:
            self._btn_a.configure(**off)
            self._btn_b.configure(**on)
        self._clear_results()

    # ── Path / drop ───────────────────────────────────────────────────────
    def _on_path_typed(self, *_):
        self._clear_results()

    def _browse(self):
        path = filedialog.askdirectory(title="Select source folder")
        if path:
            self.path_var.set(path)
            self.drop_title.configure(text=Path(path).name, fg=TEXT)

    def _on_drop(self, event):
        raw = event.data.strip()
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        path   = Path(raw)
        folder = path if path.is_dir() else path.parent
        self.path_var.set(str(folder))
        self.drop_title.configure(text=folder.name, fg=ACCENT)
        self.drop_frame.configure(highlightbackground=ACCENT)

    def _get_folder(self):
        p = self.path_var.get().strip()
        if not p:
            return None
        path = Path(p)
        return path if path.is_dir() else None

    # ── Convert ───────────────────────────────────────────────────────────
    def _on_convert(self):
        folder = self._get_folder()
        if not folder:
            messagebox.showwarning("No folder",
                                   "Paste a folder path or drop a folder first.")
            return

        direction = self._direction.get()
        in_ext    = "woff2" if direction == "woff2_to_ttf" else "ttf"
        files     = _get_files(folder, direction)

        if not files:
            messagebox.showinfo("Nothing to convert",
                                f"No .{in_ext} files found in that folder.")
            return

        # Clear previous results first, then create a fresh temp dir
        self._clear_results()

        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="fontconv_"))

        self._source_folder   = folder
        self._converted_files = []
        self._temp_out_dir    = tmp

        self.convert_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled", fg=MUTED, bg=SURFACE2)
        self.progress_var.set(0)
        self.status_var.set(f"Converting {len(files)} file(s)…")
        self.status_lbl.configure(fg=MUTED)

        threading.Thread(
            target=_run_conversion,
            args=(folder, tmp, direction, self._cb_progress, self._cb_done),
            daemon=True
        ).start()

    def _cb_progress(self, done, total):
        pct = done / total * 100
        self.root.after(0, lambda: self.progress_var.set(pct))
        self.root.after(0, lambda: self.status_var.set(f"Converting {done}/{total}…"))

    def _cb_done(self, converted, errors, out_dir):
        self._converted_files = converted

        def _update():
            self.convert_btn.configure(state="normal")
            self.progress_var.set(100 if converted else 0)

            if not converted and not errors:
                self.status_var.set("No matching files found.")
                self.status_lbl.configure(fg=MUTED)
                return

            if converted:
                self.save_btn.configure(state="normal",
                                        fg="#fff", bg=ACCENT,
                                        activebackground=ACCENT_H)
                msg = f"✓  {len(converted)} file(s) ready — click Save to choose where"
                if errors:
                    msg += f"   ({len(errors)} error(s))"
                self.status_var.set(msg)
                self.status_lbl.configure(fg=ACCENT if not errors else ERROR)
            else:
                self.status_var.set(f"All {len(errors)} file(s) failed to convert.")
                self.status_lbl.configure(fg=ERROR)

            if errors:
                messagebox.showwarning("Some errors",
                    "\n".join(errors[:15]) +
                    (f"\n…and {len(errors)-15} more" if len(errors) > 15 else ""))

        self.root.after(0, _update)

    # ── Save ──────────────────────────────────────────────────────────────
    def _on_save(self):
        if not self._converted_files:
            return

        dest = filedialog.askdirectory(title="Choose where to save converted fonts")
        if not dest:
            return

        import shutil
        dest_path = Path(dest)
        saved, failed = [], []

        for src in self._converted_files:
            target = dest_path / src.name
            if target.exists():
                stem, suffix, i = src.stem, src.suffix, 1
                while target.exists():
                    target = dest_path / f"{stem}_{i}{suffix}"
                    i += 1
            try:
                shutil.copy2(str(src), str(target))
                saved.append(target.name)
            except Exception as exc:
                failed.append(f"{src.name}: {exc}")

        if saved:
            self.status_var.set(f"✓  Saved {len(saved)} file(s) to {dest_path.name}/")
            self.status_lbl.configure(fg=ACCENT)

        if failed:
            messagebox.showwarning("Save errors", "\n".join(failed))

        self._cleanup_temp()
        self.save_btn.configure(state="disabled", fg=MUTED, bg=SURFACE2)

    # ── Helpers ───────────────────────────────────────────────────────────
    def _clear_results(self):
        self._converted_files = []
        self.progress_var.set(0)
        self.status_var.set("")
        self.save_btn.configure(state="disabled", fg=MUTED, bg=SURFACE2)
        self._cleanup_temp()

    def _cleanup_temp(self):
        if self._temp_out_dir and self._temp_out_dir.exists():
            import shutil
            try:
                shutil.rmtree(str(self._temp_out_dir))
            except Exception:
                pass
        self._temp_out_dir = None


# ── Entry point ────────────────────────────────────────────────────────────
def main():
    if _HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
