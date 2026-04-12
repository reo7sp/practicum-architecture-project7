import os
import time
import shutil
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Tuple

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


KNOWLEDGE_BASE_DIR = os.path.abspath(os.getenv("KNOWLEDGE_BASE_DIR", os.path.join(os.path.dirname(__file__), "..", "Task2", "knowledge_base")))
CHROMA_DB_DIR = os.path.abspath(os.getenv("CHROMA_DB_DIR", os.path.join(os.path.dirname(__file__), "chroma_db")))
INDEX_UPDATE_LOG = os.getenv("INDEX_UPDATE_LOG", "")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
COLLECTION_NAME = "void_chronicles_knowledge"


def load_documents(kb_dir: str) -> List[Document]:
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


def split_documents(documents: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    print(f"Разбиение на чанки (размер: {chunk_size}, перекрытие: {chunk_overlap})...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        is_separator_regex=False
    )

    chunks = text_splitter.split_documents(documents)

    per_source_counters: Dict[str, int] = {}
    for chunk in chunks:
        source = chunk.metadata.get('source', 'unknown')
        if not isinstance(source, str) or not source:
            source = 'unknown'
        local_id = per_source_counters.get(source, 0)
        per_source_counters[source] = local_id + 1
        chunk.metadata['chunk_id'] = local_id
        chunk.metadata['chunk_hash'] = hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest()
        chunk.metadata['chunk_uid'] = f"{source}:{local_id}:{chunk.metadata['chunk_hash']}"

    print(f"Создано {len(chunks)} чанков\n")
    return chunks


def create_embeddings(model_name: str) -> HuggingFaceEmbeddings:
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


def build_index(
    chunks: List[Document],
    embeddings: HuggingFaceEmbeddings,
    db_dir: str,
    collection_name: str,
) -> Tuple[Chroma, float, int, int, int]:
    print(f"Создание индекса в {db_dir}...")

    start_time = time.time()

    Path(db_dir).mkdir(parents=True, exist_ok=True)

    vectorstore = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings,
        collection_name=collection_name,
    )

    current_ids: List[str] = []
    for doc in chunks:
        chunk_uid = doc.metadata.get("chunk_uid") if isinstance(doc.metadata, dict) else None
        if not isinstance(chunk_uid, str) or not chunk_uid:
            source = doc.metadata.get("source") if isinstance(doc.metadata, dict) else None
            if not isinstance(source, str) or not source:
                source = "unknown"
            chunk_hash = doc.metadata.get("chunk_hash")
            if not isinstance(chunk_hash, str) or not chunk_hash:
                chunk_hash = hashlib.sha256(doc.page_content.encode("utf-8")).hexdigest()
            local_id = doc.metadata.get("chunk_id") if isinstance(doc.metadata, dict) else None
            if not isinstance(local_id, int):
                local_id = 0
            chunk_uid = f"{source}:{local_id}:{chunk_hash}"
        current_ids.append(hashlib.sha256(chunk_uid.encode("utf-8")).hexdigest())

    existing_ids: List[str] = []
    try:
        existing_resp = vectorstore.get(include=[])
        existing_ids = existing_resp.get("ids", []) or []
    except Exception:
        existing_ids = []

    ids_to_delete = sorted(set(existing_ids) - set(current_ids))
    added_count = len(set(current_ids) - set(existing_ids))
    if ids_to_delete:
        vectorstore.delete(ids=ids_to_delete)

    vectorstore.add_documents(chunks, ids=current_ids)

    final_ids: List[str] = []
    try:
        final_resp = vectorstore.get(include=[])
        final_ids = final_resp.get("ids", []) or []
    except Exception:
        final_ids = []

    elapsed_time = time.time() - start_time

    print(f"Индекс создан за {elapsed_time:.2f} сек\n")
    return vectorstore, elapsed_time, added_count, len(ids_to_delete), len(final_ids)


def write_log(entry: Dict[str, Any]) -> None:
    if not INDEX_UPDATE_LOG:
        return
    Path(INDEX_UPDATE_LOG).parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_UPDATE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    started_at = datetime.utcnow().isoformat() + "Z"
    start_time = time.time()
    errors = []
    log_entry = {
        "started_at": started_at,
        "knowledge_base_dir": KNOWLEDGE_BASE_DIR,
        "chroma_db_dir": CHROMA_DB_DIR,
        "documents_count": 0,
        "chunks_count": 0,
        "elapsed_sec": 0,
        "errors": errors,
    }

    print("Создание векторного индекса\n")

    try:
        documents = load_documents(KNOWLEDGE_BASE_DIR)
        if not documents:
            msg = "Документы не найдены!"
            print(msg)
            errors.append(msg)
            log_entry["finished_at"] = datetime.utcnow().isoformat() + "Z"
            log_entry["elapsed_sec"] = round(time.time() - start_time, 2)
            write_log(log_entry)
            return

        chunks = split_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
        embeddings = create_embeddings(EMBEDDING_MODEL)
        vectorstore, elapsed_time, added_chunks_count, deleted_chunks_count, final_chunks_count = build_index(
            chunks,
            embeddings,
            CHROMA_DB_DIR,
            COLLECTION_NAME,
        )

        log_entry["documents_count"] = len(documents)
        log_entry["chunks_count"] = len(chunks)
        log_entry["added_chunks_count"] = added_chunks_count
        log_entry["deleted_chunks_count"] = deleted_chunks_count
        log_entry["final_chunks_count"] = final_chunks_count
        log_entry["elapsed_sec"] = round(elapsed_time, 2)
        log_entry["finished_at"] = datetime.utcnow().isoformat() + "Z"

        print(f"\nГотово!")
        print(f"  Документов: {len(documents)}")
        print(f"  Чанков: {len(chunks)}")
        print(f"  Время: {elapsed_time:.2f} сек\n")
    except Exception as e:
        errors.append(str(e))
        log_entry["finished_at"] = datetime.utcnow().isoformat() + "Z"
        log_entry["elapsed_sec"] = round(time.time() - start_time, 2)
        raise
    finally:
        write_log(log_entry)


if __name__ == "__main__":
    main()
