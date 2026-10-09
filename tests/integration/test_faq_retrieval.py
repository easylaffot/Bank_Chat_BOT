from langchain_core.documents import Document

from app.rag.retriever import FAQRetriever


class FakeEmbeddingService:
    def embed_query(self, question):
        return [0.1, 0.2, 0.3]


class FakeCollection:
    def count(self):
        return 1

    def query(self, *, query_embeddings, n_results, include):
        assert query_embeddings == [[0.1, 0.2, 0.3]]
        assert n_results == 1
        return {
            "ids": [["warranty::chunk-0"]],
            "documents": [["Eligible laptops include a one-year manufacturer warranty."]],
            "metadatas": [[{"source": "data/faq/warranty.txt", "chunk_index": 0}]],
            "distances": [[0.12]],
        }


def test_faq_retriever_returns_relevant_document_and_source():
    retriever = FAQRetriever(
        embedding_service=FakeEmbeddingService(),
        collection=FakeCollection(),
    )
    documents = retriever.retrieve("What warranty is available?")
    assert len(documents) == 1
    assert isinstance(documents[0], Document)
    assert "one-year manufacturer warranty" in documents[0].page_content
    assert documents[0].metadata["source"] == "data/faq/warranty.txt"
