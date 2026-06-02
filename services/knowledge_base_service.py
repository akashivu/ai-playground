class KnowledgeBaseService:

    def __init__(self):

        self.documents = []

    def add_document(self,document_id: str,name: str,collection: str,):

        document = {"document_id": document_id,"name": name,"collection": collection,}

        self.documents.append(document)

        return document

    def list_documents(self):

        return self.documents

    def delete_document(self,document_id: str,):

        self.documents = [
            document
            for document in self.documents
            if document["document_id"]
            != document_id]

        return {"message":"Document deleted"}