from ingestion.pdf_renderer import render_pdf_to_images


pdf_path = "data/pdfs/test.pdf"

pages = render_pdf_to_images(
    pdf_path=pdf_path,
    output_dir="data/pages",
    dpi=150
)

print("\nPDF rendering successful!\n")

for page in pages:
    print(
        f"Page {page['page_number']}: "
        f"{page['image_path']} "
        f"({page['width']}x{page['height']})"
    )