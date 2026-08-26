from pathlib import Path
import fitz


def render_pdf(pdf_path, output_dir, dpi=150):
    """
    Render every PDF page as a high-resolution PNG image.

    Important:
    - No OCR is performed.
    - No text is extracted.
    - Each PDF page is treated purely as an image.
    """

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf_path)

    pages = []

    zoom = dpi / 72

    matrix = fitz.Matrix(zoom, zoom)

    for page_number, page in enumerate(document, start=1):

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        image_path = (
            output_dir
            / f"{pdf_path.stem}_page_{page_number:04d}.png"
        )

        pixmap.save(str(image_path))

        pages.append(
            {
                "page_number": page_number,
                "image_path": str(image_path),
                "source": pdf_path.name
            }
        )

        print(
            f"Rendered page {page_number}: "
            f"{image_path}"
        )

    document.close()

    return pages