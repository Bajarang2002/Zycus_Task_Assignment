from pathlib import Path
from typing import List, Dict, Any
import re
import hashlib

import numpy as np
import chromadb
from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL,
    CHROMA_PATH,
    KB_PATH
)

client = genai.Client(api_key=GEMINI_API_KEY)

COLLECTION_NAME = "zycus_knowledge_base"

SUPPORTED_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt"
}

PRIMARY_HYBRID_THRESHOLD = 0.20
MINIMUM_KEYWORD_THRESHOLD = 0.10

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_collection():
    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def get_knowledge_files() -> List[Path]:
    kb_folder = Path(KB_PATH)

    if not kb_folder.exists():
        print(f"ERROR: KB folder does not exist: {kb_folder}")
        return []

    files = [
        file
        for file in kb_folder.rglob("*")
        if file.is_file()
        and file.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    files.sort()

    print("\n" + "=" * 70)
    print("KNOWLEDGE BASE FILE SEARCH")
    print("=" * 70)
    print("KB PATH:", kb_folder)
    print("FOUND FILES:", len(files))

    for file in files:
        print(" -", file.relative_to(kb_folder))

    print("=" * 70)

    return files


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:
    paragraphs = re.split(r"\n\s*\n", text)

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()

        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{para}".strip()

        else:
            if current_chunk:
                chunks.append(current_chunk)

            if len(para) > chunk_size:
                words = para.split()
                sub_chunk = ""

                for word in words:
                    if len(sub_chunk) + len(word) + 1 <= chunk_size:
                        sub_chunk = f"{sub_chunk} {word}".strip()
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)

                        sub_chunk = word

                if sub_chunk:
                    current_chunk = sub_chunk

            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    if len(chunks) > 1 and overlap > 0:
        overlapped_chunks = []

        for i, chunk in enumerate(chunks):
            if i > 0:
                previous_tail = chunks[i - 1][-overlap:]
                chunk = f"{previous_tail}\n{chunk}"

            overlapped_chunks.append(chunk)

        return overlapped_chunks

    return chunks


def read_knowledge_base():
    files = get_knowledge_files()

    documents = []
    ids = []
    metadatas = []

    for file in files:
        try:
            text = file.read_text(encoding="utf-8")

        except Exception as exc:
            print(f"ERROR reading {file}: {exc}")
            continue

        if not text.strip():
            continue

        relative_path = file.relative_to(Path(KB_PATH))
        source = str(relative_path).replace("\\", "/")

        chunks = chunk_text(text)

        for index, chunk in enumerate(chunks):
            documents.append(chunk)

            chunk_id = (
                f"{source}__chunk_{index}"
                .replace("/", "_")
                .replace(".", "_")
            )

            ids.append(chunk_id)
            metadatas.append({
                "source": source
            })

    print(f"TOTAL CHUNKS GENERATED: {len(documents)}")

    return documents, ids, metadatas


def get_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    batch_size = 32
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )

        all_embeddings.extend(
            item.values
            for item in response.embeddings
        )

    return all_embeddings


def get_query_embedding(text: str) -> List[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[text],
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )
    )

    return response.embeddings[0].values


def get_kb_fingerprint() -> str:
    files = get_knowledge_files()

    hasher = hashlib.md5()

    for file in files:
        hasher.update(str(file).encode())
        hasher.update(
            str(file.stat().st_mtime_ns).encode()
        )

    return hasher.hexdigest()


def load_knowledge_base():
    collection = get_collection()

    documents, ids, metadatas = read_knowledge_base()

    if not documents:
        print("WARNING: No KB documents found.")
        return collection

    existing = collection.get(
        include=["metadatas"]
    )

    existing_metadata = existing.get(
        "metadatas",
        []
    )

    existing_sources = sorted(
        set(
            metadata.get("source", "")
            for metadata in existing_metadata
            if metadata
        )
    )

    current_sources = sorted(
        set(
            metadata["source"]
            for metadata in metadatas
        )
    )

    if (
        collection.count() > 0
        and existing_sources == current_sources
    ):
        print(
            f"Chroma contains {collection.count()} chunks. "
            "Index is up to date."
        )

        return collection

    if collection.count() > 0:
        print(
            "Knowledge base source structure changed. "
            "Rebuilding Chroma collection..."
        )

        chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        chroma_client.delete_collection(
            COLLECTION_NAME
        )

        collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    print(
        f"Creating embeddings for {len(documents)} chunks..."
    )

    embeddings = get_embeddings(documents)

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        "KB indexed successfully. "
        f"Total Chroma count: {collection.count()}"
    )

    return collection


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(
        r"[^a-z0-9_\s]",
        " ",
        text
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def keyword_score(
    query: str,
    document: str
) -> float:
    query_text = normalize_text(query)
    document_text = normalize_text(document)

    query_words = set(query_text.split())
    document_words = set(document_text.split())

    if not query_words:
        return 0.0

    stop_words = {
        "the", "is", "are", "a", "an",
        "to", "of", "our", "we", "and",
        "in", "for", "with", "on",
        "from", "this", "that", "my",
        "have", "has", "it", "can",
        "or", "as", "at", "by",
        "how", "what", "issue"
    }

    meaningful_words = query_words - stop_words

    if not meaningful_words:
        meaningful_words = query_words

    common_meaningful = (
        query_words
        & document_words
        & meaningful_words
    )

    overlap_ratio = (
        len(common_meaningful)
        / len(meaningful_words)
    )

    return float(overlap_ratio)


def search_knowledge_base(
    query: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:

    if not query.strip():
        return []

    collection = load_knowledge_base()
    count = collection.count()

    if count == 0:
        print("WARNING: Knowledge base is empty.")
        return []

    query_embedding = get_query_embedding(query)

    n_results = min(15, count)

    semantic_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = semantic_results["documents"][0]
    metadatas = semantic_results["metadatas"][0]
    distances = semantic_results["distances"][0]

    candidates = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        semantic_score = max(
            0.0,
            1.0 - (float(distance) / 2.0)
        )

        lexical_score = keyword_score(
            query,
            document
        )

        hybrid_score = (
            semantic_score * 0.75
            + lexical_score * 0.25
        )

        candidates.append({
            "text": document,
            "source": metadata.get(
                "source",
                "unknown"
            ),
            "semantic_score": semantic_score,
            "keyword_score": lexical_score,
            "relevance": hybrid_score
        })

    candidates.sort(
        key=lambda x: x["relevance"],
        reverse=True
    )

    final_results = []

    for item in candidates:
        if (
            item["relevance"]
            >= PRIMARY_HYBRID_THRESHOLD
            or item["keyword_score"]
            >= MINIMUM_KEYWORD_THRESHOLD
        ):
            final_results.append({
                "text": item["text"],
                "source": item["source"],
                "relevance": round(
                    item["relevance"],
                    4
                )
            })

    if not final_results and candidates:
        top_candidate = candidates[0]

        final_results.append({
            "text": top_candidate["text"],
            "source": top_candidate["source"],
            "relevance": round(
                top_candidate["relevance"],
                4
            )
        })

    final_results = final_results[:top_k]

    print(
        f"\nRetrieved KB results: "
        f"{len(final_results)}"
    )

    for item in final_results:
        print(
            f"SOURCE: {item['source']} | "
            f"RELEVANCE: {item['relevance']}"
        )

    return final_results