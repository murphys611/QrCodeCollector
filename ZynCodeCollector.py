"""
Batch QR decoder + slow, resumable submitter.

Setup:
    pip install opencv-python playwright
    playwright install chromium

Usage:
    1. Put all your photos in a folder called "photos" next to this script.
    2. python zyn_codes.py decode    -> reads every photo, writes codes.txt
    3. Open codes.txt and sanity-check it.
    4. python zyn_codes.py submit    -> enters each code on the site
"""
import sys
import time
import random
from pathlib import Path

import cv2
import zxingcpp

PHOTO_DIR = Path("photos")
CODES_FILE = Path("codes.txt")
DONE_FILE = Path("done.txt")  # codes already submitted, so you can resume

# ---- Fill these in after inspecting the site (right-click > Inspect) ----
ENTRY_URL = "https://www.zyn.com/us/en/zyn-rewards.html"
INPUT_SELECTOR = 'input[placeholder*="2E4CP98V0"]'
SUBMIT_SELECTOR = 'button:has-text("Submit code")'
# -------------------------------------------------------------------------

IMG_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".bmp"}


def read_codes(img):
    """Return the code from every QR in one image (ignores the barcode)."""
    found = []
    for r in zxingcpp.read_barcodes(img):
        if r.format == zxingcpp.BarcodeFormat.QRCode:
            found.append(r.text.rstrip("/").split("/")[-1])
    return found


def decode():
    files = sorted(p for p in PHOTO_DIR.iterdir() if p.suffix.lower() in IMG_EXTS)
    if not files:
        sys.exit(f"No photos found in {PHOTO_DIR}/")

    all_codes, failed = [], []
    for f in files:
        img = cv2.imread(str(f))
        if img is None:
            failed.append(f.name)
            continue
        found = read_codes(img)
        if not found:
            failed.append(f.name)
        all_codes.extend(found)
        print(f"{f.name}: {len(found)} code(s)")

    # de-duplicate but keep order
    unique = list(dict.fromkeys(all_codes))
    CODES_FILE.write_text("\n".join(unique))
    print(f"\n{len(unique)} unique codes saved to {CODES_FILE}")
    if failed:
        print("No code read from:", ", ".join(failed))


def submit():
    from playwright.sync_api import sync_playwright

    codes = CODES_FILE.read_text().split()
    done = set(DONE_FILE.read_text().split()) if DONE_FILE.exists() else set()
    todo = [c for c in codes if c not in done]
    print(f"{len(todo)} codes to submit ({len(done)} already done)")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        entry = page.url
        print("Using page:", entry)

        for i, code in enumerate(todo, 1):
            try:
                page.goto(entry)
                if "login" in page.url.lower():
                    raise Exception("Got sent back to login, session expired")
                page.fill(INPUT_SELECTOR, code)
                page.click(SUBMIT_SELECTOR)
                page.wait_for_timeout(random.randint(3000, 8000))
            except Exception as e:
                print(f"Stopped on code {i}: {e}")
                break
            with DONE_FILE.open("a") as f:
                f.write(code + "\n")
            print(f"[{i}/{len(todo)}] submitted {code}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("decode", "submit"):
        sys.exit("Usage: python zyn_codes.py decode|submit")
    decode() if sys.argv[1] == "decode" else submit()