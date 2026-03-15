import time
import shutil
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

KNOWLEDGE_BASE_DIR = "../Task2/knowledge_base"
CHROMA_DB_DIR = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
COLLECTION_NAME = "void_chronicles_knowledge"

def load_documents(kb_dir: str):
    documents = []
    kb_path = Path(kb_dir)

    print(f"Загрузка документов из {kb_dir}...")

    for file_path in sorted(kb_path.glob("*.txt")):
        try:
            loader = TextLoader(str(file_path), encoding='utf-8')
            docs = loader.load()

            for doc in docs:
                doc.metadata['source'] = file_path.name
                doc.metadata['title'] = file_path.stem

            documents.extend(docs)
            print(f"  + {file_path.name}")
        except Exception as e:
            print(f"  - {file_path.name}: {e}")

    print(f"Загружено {len(documents)} документов\n")
    return documents


def split_documents(documents, chunk_size: int, chunk_overlap: int):
    print(f"Разбиение на чанки (размер: {chunk_size}, перекрытие: {chunk_overlap})...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        is_separator_regex=False
    )

    chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata['chunk_id'] = i

    print(f"Создано {len(chunks)} чанков\n")
    return chunks


def create_embeddings(model_name: str):
    print(f"Инициализация модели: {model_name}")
    print(f"  Репозиторий: https://huggingface.co/{model_name}")
    print(f"  Размер эмбеддингов: 384 измерения")

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    print(f"Модель готова\n")
    return embeddings


def build_index(chunks, embeddings, db_dir: str, collection_name: str):
    print(f"Создание индекса в {db_dir}...")

    if Path(db_dir).exists():
        shutil.rmtree(db_dir)

    start_time = time.time()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_dir,
        collection_name=collection_name
    )

    elapsed_time = time.time() - start_time

    print(f"Индекс создан за {elapsed_time:.2f} сек\n")
    return vectorstore, elapsed_time


def main():
    print("Создание векторного индекса\n")

    documents = load_documents(KNOWLEDGE_BASE_DIR)
    if not documents:
        print("Документы не найдены!")
        return

    chunks = split_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
    embeddings = create_embeddings(EMBEDDING_MODEL)
    vectorstore, elapsed_time = build_index(chunks, embeddings, CHROMA_DB_DIR, COLLECTION_NAME)

    print(f"\nГотово!")
    print(f"  Документов: {len(documents)}")
    print(f"  Чанков: {len(chunks)}")
    print(f"  Время: {elapsed_time:.2f} сек\n")


if __name__ == "__main__":
    main()
