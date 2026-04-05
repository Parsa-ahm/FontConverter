# Font Converter

A lightweight desktop app for converting fonts between **WOFF2** and **TTF** formats — built with Python and tkinter, distributed as a single `.exe` with no install required.

![Font Converter Screenshot](https://raw.githubusercontent.com/placeholder/font-converter/main/preview.png)

---

## Why I Built This

My TTF font files got corrupted but the WOFF2 versions were still intact. I needed a quick, shareable tool to batch-convert them back — without hunting for online converters or installing heavy software. So I built one.

---

## Features

- **Drag & drop** a folder onto the app — or paste/type a path, or click Browse
- **Bidirectional** — convert WOFF2 → TTF *or* TTF → WOFF2
- **Batch conversion** — processes every font in a folder, including subfolders
- **Choose your output location** — converted files are staged first, then you pick where to save
- **Progress bar** with live file count
- **Collision handling** — auto-renames if a file already exists at the destination
- Single `.exe` — no Python, no installs needed to run

---

## Download

Grab the latest `FontConverter.exe` from [**Releases**](../../releases).

Drop it anywhere and run it — no installer, no setup.

---

## Usage

1. Run `FontConverter.exe`
2. Select a direction: **WOFF2 → TTF** or **TTF → WOFF2**
3. Drop a folder onto the zone, paste a path, or click **Browse**
4. Click **Convert**
5. Click **Save to…** and pick where the converted fonts should go

---

## Building from Source

Requires **Python 3.9+** and **pip**.

```bash
git clone https://github.com/yourusername/font-converter.git
cd font-converter
```

Then double-click `build.bat` — it will:

1. Install all dependencies (`fonttools`, `brotli`, `tkinterdnd2`, `pyinstaller`)
2. Bundle everything into `dist/FontConverter.exe`

Or run it manually:

```bash
pip install fonttools brotli tkinterdnd2 pyinstaller
python converter.py
```

---

## Dependencies

| Package | Purpose |
|---|---|
| [fonttools](https://github.com/fonttools/fonttools) | Font parsing and format conversion |
| [brotli](https://github.com/google/brotli) | WOFF2 decompression |
| [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) | Drag & drop support for tkinter |
| [pyinstaller](https://pyinstaller.org) | Packages the app into a single `.exe` |

---

## License

MIT — do whatever you want with it.
