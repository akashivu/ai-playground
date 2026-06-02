from embeddings.embedding_service import (get_embedding,)

from loaders.pdf_loader import (load_pdf,)

from utils.text_cleaner import (clean_text,)

from utils.text_splitter import (split_chunks,)


class DocumentService:

    def __init__(self,vector_store,bm25_service):

        self.vector_store = (vector_store)
        self.bm25_service = (bm25_service)

    def process_document(self,file_path: str,document_id: str,collection: str,):

        text = load_pdf(file_path)

        text = clean_text(text)

        chunks = split_chunks(text)

        embeddings = []

        metadata = []

        for chunk in chunks:

            embedding = (get_embedding(chunk))

            embeddings.append(embedding)

            metadata.append({"text": chunk,"source": file_path,"document_id": document_id,"collection": collection,})

        self.vector_store.add_documents(embeddings,metadata,)
        self.vector_store.save_index("faiss.index")

        self.vector_store.save_metadata("metadata.json")
        self.bm25_service.add_documents([item["text"] for item in metadata])

        return {"status": "success","chunks": len(chunks),}