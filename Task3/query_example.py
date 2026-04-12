from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="void_chronicles_knowledge"
)

query = "What is the Synth and how do Sentinels use it?"
results = vectorstore.similarity_search(query, k=3)

print(f"Query: {query}\n")
for i, doc in enumerate(results, 1):
    print(f"Result {i}:")
    print(f"  Source: {doc.metadata['source']}")
    print(f"  Chunk ID: {doc.metadata['chunk_id']}")
    print(f"  Text: {doc.page_content[:200]}...\n")
