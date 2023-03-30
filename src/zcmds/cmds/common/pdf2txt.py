"""
Converts a pdf to a list of strings, one for each page.
"""

from argparse import ArgumentParser

import PyPDF2  # type: ignore


def read_pdf_pages(pdf: str) -> list[str]:
    """Reads pdfs and returns a list of strings, one for each page."""
    # Open the PDF file in read-binary mode
    with open(pdf, "rb") as pdf_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Get the total number of pages in the PDF document
        num_pages = len(pdf_reader.pages)

        out: list[str] = []
        # Loop through each page and extract the text using PyPDF2
        for page_num in range(num_pages):
            page_obj = pdf_reader.pages[page_num]
            page_text = page_obj.extract_text()

            # Print the extracted text for this page
            out.append(page_text)
        return out


def main() -> None:
    """Main."""
    parser = ArgumentParser()
    parser.add_argument("input_pdf", help="input")
    args = parser.parse_args()
    # print(args)
    pages: list[str] = read_pdf_pages(args.input_pdf)
    for page in pages:
        print(page)


if __name__ == "__main__":
    main()
