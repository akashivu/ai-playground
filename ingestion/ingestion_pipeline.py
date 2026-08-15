from embeddings.ingestion.pdf_loader import load_pdf
from embeddings.ingestion.text_cleaner import clean_text
from embeddings.ingestion.chunker import split_chunks


def process_document(pdf_path: str):

    text = load_pdf(pdf_path)

    text = clean_text(text)

    chunks = split_chunks(text)

    processed_chunks = []

    for index, chunk in enumerate(chunks):

        processed_chunks.append({"chunk_id": index, "source": pdf_path, "text": chunk})

    return processed_chunks
