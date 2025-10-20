import shutil
import time
import ctypes
from pathlib import Path

IMAGE_NAME = "rat.jpg"
PUBLIC_DOWNLOADS = Path(r"C:\Users\Public\Downloads")
CHECK_INTERVAL = 0.5
ZERO_WIDTH = "\u200B"


def refresh_desktop():
    """Force Windows Explorer to refresh the desktop once."""
    try:
        ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)
    except Exception:
        pass


def get_desktop_path() -> Path:
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop
    alt = Path(r"C:\Users\Public\Desktop")
    if alt.exists():
        return alt
    return Path.home()


def ensure_source_image() -> Path:
    src = PUBLIC_DOWNLOADS / IMAGE_NAME
    if not src.exists():
        PUBLIC_DOWNLOADS.mkdir(parents=True, exist_ok=True)
        with open(src, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\nRAT_PLACEHOLDER")
    return src


def make_invisible_name(base: str, count: int) -> str:
    return ZERO_WIDTH * count + base


def copy_rat(count: int) -> str:
    """Copy rat.jpg to Desktop with invisible counter."""
    source = ensure_source_image()
    name = make_invisible_name(IMAGE_NAME, count)
    dest = get_desktop_path() / name
    try:
        shutil.copy2(source, dest)
        return name
    except Exception:
        return ""


def list_desktop_files() -> set:
    desktop = get_desktop_path()
    try:
        return {f.name for f in desktop.iterdir() if f.is_file()}
    except Exception:
        return set()


def main():
    tracked_files = []
    counter = 1

    # Place first rat
    name = copy_rat(counter)
    if name:
        tracked_files.append(name)
        counter += 1

    try:
        while True:
            desktop_files = list_desktop_files()
            deleted = [f for f in tracked_files if f not in desktop_files]

            if deleted:
                time.sleep(0.2)  # small delay
                refreshed = list_desktop_files()
                deleted = [f for f in deleted if f not in refreshed]
                if not deleted:
                    continue

                new_copies = []

                # Replace each deleted file with two new copies
                for _ in deleted:
                    for _ in range(2):
                        name = copy_rat(counter)
                        if name:
                            new_copies.append(name)
                            counter += 1

                # Update tracked files
                tracked_files = [f for f in tracked_files if f not in deleted]
                tracked_files.extend(new_copies)

                # Refresh desktop only once after all new copies
                if new_copies:
                    refresh_desktop()

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
