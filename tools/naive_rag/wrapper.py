"""Naive RAG baseline using ChromaDB + LangChain text splitter."""

import json
import time
from pathlib import Path

import anthropic

from tools.base import ToolWrapper
from benchmarks.models import SetupResult, CompileResult, QueryResult, LintResult


class NaiveRAGWrapper(ToolWrapper):
    def __init__(self):
        self._collection = None
        self._client = None

    @property
    def name(self) -> str:
        return "naive-rag"

    @property
    def version(self) -> str:
        try:
            import importlib.metadata
            return f"chromadb-{importlib.metadata.version('chromadb')}"
        except Exception:
            return "unknown"

    def setup(self) -> SetupResult:
        start = time.monotonic()
        try:
            import chromadb
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            self._client = chromadb.Client()
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=True)
        except ImportError as e:
            elapsed = time.monotonic() - start
            return SetupResult(elapsed_seconds=elapsed, success=False, error=str(e))

    def compile(self, raw_dir: Path, wiki_dir: Path) -> CompileResult:
        """Chunk all files and embed into ChromaDB (in-memory)."""
        start = time.monotonic()
        try:
            import chromadb
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            if self._client is None:
                self._client = chromadb.Client()

            # Delete existing collection if any
            try:
                self._client.delete_collection("benchmark")
            except Exception:
                pass

            self._collection = self._client.create_collection(
                name="benchmark",
                metadata={"hnsw:space": "cosine"}
            )

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )

            all_chunks = []
            all_ids = []
            all_metadatas = []
            chunk_id = 0

            for fpath in sorted(raw_dir.rglob("*")):
                if not fpath.is_file():
                    continue
                # Skip binary files
                if fpath.suffix in [".pyc", ".so", ".o", ".png", ".jpg", ".gif", ".whl"]:
                    continue

                try:
                    text = fpath.read_text(errors="ignore")
                except Exception:
                    continue

                if not text.strip():
                    continue

                chunks = splitter.split_text(text)
                for chunk in chunks:
                    all_chunks.append(chunk)
                    all_ids.append(f"chunk_{chunk_id}")
                    all_metadatas.append({
                        "source": str(fpath.relative_to(raw_dir)),
                        "chunk_index": chunk_id,
                    })
                    chunk_id += 1

            # ChromaDB batches max 41666 docs at a time
            batch_size = 5000
            for i in range(0, len(all_chunks), batch_size):
                end = min(i + batch_size, len(all_chunks))
                self._collection.add(
                    documents=all_chunks[i:end],
                    ids=all_ids[i:end],
                    metadatas=all_metadatas[i:end],
                )

            elapsed = time.monotonic() - start

            # Save chunk count as metadata
            wiki_dir.mkdir(parents=True, exist_ok=True)
            meta = {
                "total_chunks": len(all_chunks),
                "total_files": len(set(m["source"] for m in all_metadatas)),
                "chunk_size": 1000,
                "chunk_overlap": 200,
            }
            (wiki_dir / "metadata.json").write_text(json.dumps(meta, indent=2))

            output_size = sum(
                f.stat().st_size for f in wiki_dir.rglob("*") if f.is_file()
            )

            return CompileResult(
                elapsed_seconds=elapsed,
                input_tokens=0,  # ChromaDB uses its own embedding model
                output_tokens=0,
                output_size_bytes=output_size,
                success=True,
            )
        except Exception as e:
            elapsed = time.monotonic() - start
            return CompileResult(
                elapsed_seconds=elapsed, input_tokens=0, output_tokens=0,
                output_size_bytes=0, success=False, error=str(e)
            )

    def query(self, question: str) -> QueryResult:
        start = time.monotonic()
        try:
            if self._collection is None:
                return QueryResult(
                    elapsed_seconds=0, input_tokens=0, output_tokens=0,
                    answer="", cited_sources=[], success=False,
                    error="Collection not initialized. Run compile first."
                )

            # Retrieve top 5 chunks
            results = self._collection.query(
                query_texts=[question],
                n_results=5,
            )

            chunks = results["documents"][0] if results["documents"] else []
            sources = [
                m["source"] for m in (results["metadatas"][0] if results["metadatas"] else [])
            ]

            # Build context from retrieved chunks
            context = "\n\n---\n\n".join(chunks)

            # Use Claude to synthesize answer from retrieved context
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"Based on the following context, answer this question: {question}\n\nContext:\n{context}\n\nAnswer concisely with specific details from the context."
                }],
            )

            answer = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            elapsed = time.monotonic() - start

            return QueryResult(
                elapsed_seconds=elapsed,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                answer=answer,
                cited_sources=list(set(sources)),
                success=True,
            )
        except Exception as e:
            elapsed = time.monotonic() - start
            return QueryResult(
                elapsed_seconds=elapsed, input_tokens=0, output_tokens=0,
                answer="", cited_sources=[], success=False, error=str(e)
            )

    def lint(self) -> LintResult:
        return LintResult(
            elapsed_seconds=0, issues_found=0, issues=[],
            success=True, supported=False
        )
