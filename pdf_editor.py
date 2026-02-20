import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk


class PDFEditorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF Editor")
        self.root.geometry("1200x800")

        self.doc: fitz.Document | None = None
        self.current_page_index = 0
        self.current_scale = 1.2
        self.tk_image: ImageTk.PhotoImage | None = None
        self.mode = tk.StringVar(value="view")
        self.status = tk.StringVar(value="Open a PDF to start editing.")

        self._build_ui()

    def _build_ui(self) -> None:
        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)

        tk.Button(top, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Save As", command=self.save_pdf).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Prev", command=self.prev_page).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Next", command=self.next_page).pack(side=tk.LEFT, padx=4)

        tk.Label(top, text="Zoom").pack(side=tk.LEFT, padx=(20, 4))
        self.zoom_slider = tk.Scale(
            top,
            from_=0.5,
            to=3.0,
            orient=tk.HORIZONTAL,
            resolution=0.1,
            length=150,
            command=self.on_zoom_change,
        )
        self.zoom_slider.set(self.current_scale)
        self.zoom_slider.pack(side=tk.LEFT)

        tk.Label(top, text="Mode:").pack(side=tk.LEFT, padx=(20, 4))
        for txt, val in [("View", "view"), ("Insert Text", "text"), ("Whiteout", "whiteout")]:
            tk.Radiobutton(top, text=txt, variable=self.mode, value=val).pack(side=tk.LEFT)

        self.page_label = tk.Label(top, text="Page: -/-")
        self.page_label.pack(side=tk.RIGHT, padx=8)

        self.canvas = tk.Canvas(self.root, bg="#444")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        bottom = tk.Label(self.root, textvariable=self.status, anchor="w")
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)

    def open_pdf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        try:
            self.doc = fitz.open(path)
            self.current_page_index = 0
            self.status.set(f"Opened: {path}")
            self.render_current_page()
        except Exception as exc:
            messagebox.showerror("Open Failed", f"Could not open PDF.\n\n{exc}")

    def save_pdf(self) -> None:
        if not self.doc:
            messagebox.showinfo("No File", "Open a PDF before saving.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="edited.pdf",
        )
        if not path:
            return

        try:
            self.doc.save(path)
            self.status.set(f"Saved: {path}")
            messagebox.showinfo("Saved", f"Saved edited PDF to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Save Failed", f"Could not save PDF.\n\n{exc}")

    def prev_page(self) -> None:
        if self.doc and self.current_page_index > 0:
            self.current_page_index -= 1
            self.render_current_page()

    def next_page(self) -> None:
        if self.doc and self.current_page_index < len(self.doc) - 1:
            self.current_page_index += 1
            self.render_current_page()

    def on_zoom_change(self, value: str) -> None:
        self.current_scale = float(value)
        self.render_current_page()

    def render_current_page(self) -> None:
        if not self.doc:
            return

        page = self.doc[self.current_page_index]
        mat = fitz.Matrix(self.current_scale, self.current_scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.tk_image = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        self.page_label.config(text=f"Page: {self.current_page_index + 1}/{len(self.doc)}")

    def on_canvas_click(self, event: tk.Event) -> None:
        if not self.doc:
            return

        page = self.doc[self.current_page_index]
        x = event.x / self.current_scale
        y = event.y / self.current_scale

        if self.mode.get() == "text":
            self.insert_text(page, x, y)
        elif self.mode.get() == "whiteout":
            self.whiteout_area(page, x, y)

    def insert_text(self, page: fitz.Page, x: float, y: float) -> None:
        text = simpledialog.askstring("Insert Text", "Text to insert:")
        if not text:
            return

        size = simpledialog.askinteger("Font Size", "Font size:", initialvalue=12, minvalue=6, maxvalue=128)
        if not size:
            return

        page.insert_text((x, y), text, fontsize=size, color=(0, 0, 0))
        self.status.set(f"Inserted text on page {self.current_page_index + 1} at ({int(x)}, {int(y)}).")
        self.render_current_page()

    def whiteout_area(self, page: fitz.Page, x: float, y: float) -> None:
        width = simpledialog.askinteger("Whiteout Width", "Rectangle width:", initialvalue=140, minvalue=10, maxvalue=2000)
        height = simpledialog.askinteger("Whiteout Height", "Rectangle height:", initialvalue=30, minvalue=10, maxvalue=2000)
        if not width or not height:
            return

        rect = fitz.Rect(x, y, x + width, y + height)
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
        self.status.set(
            f"Applied whiteout on page {self.current_page_index + 1}: ({int(x)}, {int(y)}) {width}x{height}."
        )
        self.render_current_page()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()
