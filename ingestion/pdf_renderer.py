import fitz
from pathlib import Path


def render_pdf_to_images(pdf_path, output_dir="data/pages", dpi=150):
    """
    Convert every PDF page into a PNG image.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Directory where page images will be saved.
        dpi: Rendering resolution.

    Returns:
        List of dictionaries containing page information.
    """

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = fitz.open(pdf_path)

    pages = []

    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    for page_number, page in enumerate(document):
        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        image_path = output_dir / f"page_{page_number + 1}.png"

        pixmap.save(image_path)

        pages.append(
            {
                "page_number": page_number + 1,
                "image_path": str(image_path),
                "width": pixmap.width,
                "height": pixmap.height,
            }
        )

    document.close()

    return pages