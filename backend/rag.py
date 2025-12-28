import os
import json
import sqlite3
import numpy as np
import google.generativeai as genai
from pypdf import PdfReader
import contextlib
from project_config import Config
from backend.database import Database

class RAGEngine:
    def __init__(self):
        genai.configure(api_key=Config().GOOGLE_API_KEY)
        self.embed_model = "models/text-embedding-004"
        self.db = Database()
        self.vault_dir = os.path.join(Config().ASSETS_DIR, "vault")

    def _get_db_connection(self):
        """Helper to get a fresh connection directly"""
        return sqlite3.connect(Config().DB_PATH)

    def _recursive_chunk(self, text, chunk_size=1000, overlap=100):
        """
        Splits text into chunks respecting sentence boundaries where possible.
        """
        if len(text) <= chunk_size:
            return [text]
            
        chunks = []
        start = 0
        
        # Simple sentence splitters
        delimiters = [". ", "? ", "! ", "\n\n", "\n", " "]
        
        while start < len(text):
            # If remaining text fits, add it
            if len(text) - start <= chunk_size:
                chunks.append(text[start:])
                break
                
            # Find best cut point
            end = start + chunk_size
            cut_point = -1
            
            # Look for delimiters in reverse order of priority
            file_slice = text[start:end]
            
            for d in delimiters:
                last_pos = file_slice.rfind(d)
                if last_pos != -1:
                    cut_point = start + last_pos + len(d)
                    break
            
            # If no good delimiter found, hard cut
            if cut_point == -1:
                cut_point = end
                
            chunks.append(text[start:cut_point])
            start = cut_point - overlap # Backtrack for overlap
            
        return chunks

    def ingest_vault(self):
        """
        Scans the vault, chunks documents, embeds them in BATCHES, and stores in DB.
        Optimized for cost (Incremental Indexing) and speed (Batching).
        """
        if not os.path.exists(self.vault_dir):
            os.makedirs(self.vault_dir, exist_ok=True)
            return "Vault directory created. Please add documents."
            
        processed_files = 0
        total_chunks = 0
        errors = 0
        BATCH_SIZE = 50

        # --- 1. Incremental Indexing Strategy ---
        # Get list of files already in DB to avoid re-embedding
        with contextlib.closing(self._get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT filename FROM embeddings")
            existing_files = {row[0] for row in cursor.fetchall()}

        # Scan directory
        current_files = set([f for f in os.listdir(self.vault_dir) if os.path.isfile(os.path.join(self.vault_dir, f))])
        
        # A. Cleanup Removed Files
        files_to_remove = existing_files - current_files
        if files_to_remove:
            print(f"Removing {len(files_to_remove)} orphaned files from Index...")
            with contextlib.closing(self._get_db_connection()) as conn:
                cursor = conn.cursor()
                for f in files_to_remove:
                    cursor.execute("DELETE FROM embeddings WHERE filename=?", (f,))
                conn.commit()

        # B. Identify New/Modified Files
        # (For MVP, we assume filename uniqueness = identity. 
        #  Production would check hashmaps or mtime)
        files_to_process = list(current_files - existing_files)
        
        if not files_to_process:
            return f"Index is up to date. Verified {len(current_files)} documents."

        print(f"Processing {len(files_to_process)} new documents...")
        
        # --- 2. Chunking & Preparation ---
        batch_texts = []
        batch_metadata = [] # List of (filename, page_num, text_content)

        for filename in files_to_process:
            file_path = os.path.join(self.vault_dir, filename)
            doc_chunks = [] # List of (text, page_num)
            
            try:
                if filename.lower().endswith('.pdf'):
                    reader = PdfReader(file_path)
                    for i, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            page_chunks = self._recursive_chunk(page_text)
                            for c in page_chunks:
                                doc_chunks.append((c, i+1))
                                
                elif filename.lower().endswith(('.txt', '.md')):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                        if text_content:
                            raw_chunks = self._recursive_chunk(text_content)
                            for c in raw_chunks:
                                doc_chunks.append((c, 1))
                else:
                    continue 

                # Add to batch queue
                for text, page in doc_chunks:
                    batch_texts.append(text)
                    batch_metadata.append((filename, page, text))
                
                processed_files += 1
                
            except Exception as e:
                print(f"Failed to read {filename}: {e}")
                errors += 1
                continue

        if not batch_texts:
             return "No valid text found in new files."

        # --- 3. Batch Embedding & Storage ---
        print(f"Embedding {len(batch_texts)} chunks in batches of {BATCH_SIZE}...")
        
        # Iterate in batches
        for i in range(0, len(batch_texts), BATCH_SIZE):
            batch_slice = batch_texts[i : i + BATCH_SIZE]
            metadata_slice = batch_metadata[i : i + BATCH_SIZE]
            
            try:
                # ONE API call for up to 50 chunks
                embedding_result = genai.embed_content(
                    model=self.embed_model,
                    content=batch_slice,
                    task_type="retrieval_document"
                )
                embeddings = embedding_result['embedding']
                
                # Verify alignment
                if len(embeddings) != len(batch_slice):
                    print(f"Warning: Batch mismatch. Sent {len(batch_slice)}, got {len(embeddings)}")
                    continue
                
                # Insert Batch
                with contextlib.closing(self._get_db_connection()) as conn:
                    cursor = conn.cursor()
                    
                    for idx, vector in enumerate(embeddings):
                        fname, pg, txt = metadata_slice[idx]
                        stored_content = f"[File: {fname} | Page: {pg}]\n{txt}"
                        
                        cursor.execute(
                            "INSERT INTO embeddings (filename, chunk_index, content, embedding_json) VALUES (?, ?, ?, ?)",
                            (fname, pg, stored_content, json.dumps(vector))
                        )
                    conn.commit()
                
                total_chunks += len(batch_slice)
                
            except Exception as e:
                print(f"Batch embedding failed: {e}")
                errors += 1

        return f"Ingestion Complete: {processed_files} new files, {total_chunks} chunks added. ({errors} errors)"

    def retrieve(self, query, top_k=5, score_threshold=0.6):
        """
        Retrieves top_k relevant context chunks for the query.
        Filters by score_threshold to reduce hallucinations.
        """
        try:
            # Embed query
            embedding_result = genai.embed_content(
                model=self.embed_model,
                content=query,
                task_type="retrieval_query"
            )
            query_vector = np.array(embedding_result['embedding'])
            
            # Fetch all embeddings (Naive scan)
            results = []
            with contextlib.closing(self._get_db_connection()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT content, embedding_json, filename FROM embeddings")
                rows = cursor.fetchall()
                
                for row in rows:
                    vec = np.array(json.loads(row['embedding_json']))
                    # Cosine Similarity
                    norm_q = np.linalg.norm(query_vector)
                    norm_v = np.linalg.norm(vec)
                    
                    if norm_q == 0 or norm_v == 0:
                        continue
                        
                    similarity = np.dot(query_vector, vec) / (norm_q * norm_v)
                    
                    if similarity >= score_threshold:
                        results.append({
                            "content": row['content'],
                            "filename": row['filename'],
                            "score": float(similarity)
                        })
            
            # Sort by score desc
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []
