from pypdf import PdfReader


def load_pdf(path: str):

    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        extracted_text = page.extract_text()

        if extracted_text:
            text += extracted_text + "\n"

    return text
