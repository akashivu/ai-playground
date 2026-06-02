from embeddings.embedding_service import (get_embedding,)

from loaders.pdf_loader import (load_pdf,)

from utils.text_cleaner import (clean_text,)

from utils.text_splitter import (split_chunks,)


class DocumentService:

    def __init__(self,vector_store,):

        self.vector_store = (vector_store)

    def process_document(self,file_path: str,):

        text = load_pdf(file_path)

        text = clean_text(text)

        chunks = split_chunks(text)

        embeddings = []

        metadata = []

        for chunk in chunks:

            embedding = (get_embedding(chunk))

            embeddings.append(embedding)

            metadata.append({"text": chunk,"source": file_path,})

        self.vector_store.add_documents(embeddings,metadata,)

        return {"status": "success","chunks": len(chunks),}