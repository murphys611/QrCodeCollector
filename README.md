# QR Batch Decoder

A small Python command-line tool that reads every image in a folder, finds the QR codes in each one, and saves the decoded results to a text file. Built to replace scanning dozens of QR codes one at a time with a phone.

## Features

- Decodes QR codes from a whole folder of photos in one run
- Handles several QR codes per photo
- Ignores linear barcodes (EAN/UPC) that appear next to the QR code
- Removes duplicates and keeps the original order
- Reports which photos had no readable code, so you know what to retake
- Optional `--last-segment` flag extracts just the ID from URL-style payloads (e.g. `https://example.com/ABC123` becomes `ABC123`)

## Requirements

- Python 3.9+
- [opencv-python](https://pypi.org/project/opencv-python/) and [zxing-cpp](https://pypi.org/project/zxing-cpp/)

```
python -m pip install opencv-python zxing-cpp
```

## Usage

1. Put your photos in a folder named `photos` next to the script.
2. Run:

```
python qr_batch_decoder.py
```

Results are written to `codes.txt`, one per line.

Options:

```
python qr_batch_decoder.py my_images            # use a different folder
python qr_batch_decoder.py -o results.txt       # use a different output file
python qr_batch_decoder.py --last-segment       # keep only text after the last "/"
```

Example output:

```
IMG_0001.jpg: 1 code(s)
IMG_0002.jpg: 1 code(s)
IMG_0003.jpg: 0 code(s)

2 unique codes saved to codes.txt
No code read from: IMG_0003.jpg
```

## Tips for reliable reads

- Use JPG or PNG. iPhone HEIC files are not supported by OpenCV; switch the camera to Most Compatible or export as JPG.
- Keep the code flat, sharp, and evenly lit, without glare.
- Small codes read fine in a full-size photo, but the more codes in one frame, the larger each needs to be. Check that the unique count matches what you expect.

## Why zxing-cpp?

OpenCV's built-in `QRCodeDetector` missed small, slightly blurry codes in handheld photos during testing. zxing-cpp decoded the same photos reliably.

## Notes

- Decoded contents are saved exactly as printed, so case matters.
- Only scan codes you own or have permission to process.

## License

MIT
