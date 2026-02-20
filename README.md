# PDF Editor (Windows, Python)

A lightweight desktop PDF editor built with **Python + Tkinter + PyMuPDF**.

## Features

- Open and view PDF files
- Navigate pages (Prev / Next)
- Zoom from 50% to 300%
- Insert text by clicking on the page
- Whiteout (cover/redact visually) an area by clicking and specifying rectangle size
- Save edited output as a new PDF

## Requirements

- Python 3.10+
- Windows (works on Linux/macOS too)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python pdf_editor.py
```

## How to edit

1. Click **Open PDF**.
2. Choose mode:
   - **Insert Text**: click where you want text, then enter text + font size.
   - **Whiteout**: click top-left of the area, then enter width + height.
3. Click **Save As** to export edited PDF.

## Notes

- Whiteout draws a white rectangle over content. It is a visual cover, not secure redaction.
- For true irreversible redaction, PyMuPDF supports dedicated redaction APIs that can be added later.
