"""
Jarvis OS Codebase Semantic RAG Engine
Parses source code into semantic blocks (functions, classes, structs)
and builds a local full-text and symbol search index using SQLite FTS5.
"""

import os
import re
import sys
import sqlite3
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("jarvis.code_rag")

IGNORED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    "target", "dist", "build", ".idea", ".vscode"
}

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".go": "go",
    ".js": "javascript",
    ".ts": "typescript",
    ".sh": "bash",
    ".md": "markdown"
}

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "code_index.db")

class CodeRAG:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS code_chunks (
                id INTEGER PRIMARY KEY,
                file_path TEXT,
                language TEXT,
                symbol_name TEXT,
                start_line INTEGER,
                end_line INTEGER,
                content TEXT
            )
        """)
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS code_fts USING fts5(
                file_path, symbol_name, content, content='code_chunks', content_rowid='id'
            )
        """)
        conn.commit()
        conn.close()

    def chunk_file(self, file_path: str, lang: str) -> List[Dict[str, Any]]:
        """Splits file into logical code blocks by functions, classes, or paragraph."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            return []

        chunks = []
        current_chunk = []
        current_symbol = "module"
        start_line = 1

        # Heuristic chunking for functions and classes
        symbol_pattern = re.compile(
            r"^\s*(def |class |fn |struct |impl |func |async function |function )\s*([a-zA-Z0-9_]+)"
        )

        for i, line in enumerate(lines, start=1):
            match = symbol_pattern.match(line)
            if match:
                if current_chunk:
                    chunks.append({
                        "file_path": file_path,
                        "language": lang,
                        "symbol_name": current_symbol,
                        "start_line": start_line,
                        "end_line": i - 1,
                        "content": "".join(current_chunk).strip()
                    })
                    current_chunk = []
                current_symbol = match.group(2)
                start_line = i

            current_chunk.append(line)

            # Cap chunks at ~100 lines if no new symbol is encountered
            if len(current_chunk) >= 100:
                chunks.append({
                    "file_path": file_path,
                    "language": lang,
                    "symbol_name": current_symbol,
                    "start_line": start_line,
                    "end_line": i,
                    "content": "".join(current_chunk).strip()
                })
                current_chunk = []
                start_line = i + 1

        if current_chunk:
            chunks.append({
                "file_path": file_path,
                "language": lang,
                "symbol_name": current_symbol,
                "start_line": start_line,
                "end_line": len(lines),
                "content": "".join(current_chunk).strip()
            })

        return chunks

    def index_directory(self, target_dir: str) -> int:
        """Indexes all supported source files in target directory."""
        target_dir = os.path.abspath(target_dir)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        indexed_count = 0
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in SUPPORTED_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    lang = SUPPORTED_EXTENSIONS[ext]
                    chunks = self.chunk_file(file_path, lang)
                    for c in chunks:
                        cur.execute(
                            "INSERT INTO code_chunks (file_path, language, symbol_name, start_line, end_line, content) VALUES (?, ?, ?, ?, ?, ?)",
                            (c["file_path"], c["language"], c["symbol_name"], c["start_line"], c["end_line"], c["content"])
                        )
                        chunk_id = cur.lastrowid
                        cur.execute(
                            "INSERT INTO code_fts (rowid, file_path, symbol_name, content) VALUES (?, ?, ?, ?)",
                            (chunk_id, c["file_path"], c["symbol_name"], c["content"])
                        )
                        indexed_count += 1

        conn.commit()
        conn.close()
        logger.info(f"Indexed {indexed_count} code chunks in {target_dir}.")
        return indexed_count

    def search_code(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches code chunks matching natural language or code symbols."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        words = re.findall(r"\w+", query)
        if not words:
            conn.close()
            return []

        match_query = " OR ".join([f'"{w}"*' for w in words[:6]])
        try:
            cur.execute("""
                SELECT c.file_path, c.language, c.symbol_name, c.start_line, c.end_line, c.content, rank
                FROM code_fts(?) fts
                JOIN code_chunks c ON c.id = fts.rowid
                ORDER BY rank
                LIMIT ?
            """, (match_query, top_k))
            rows = cur.fetchall()
        except Exception:
            rows = []

        conn.close()

        results = []
        for r in rows:
            results.append({
                "file_path": r[0],
                "language": r[1],
                "symbol_name": r[2],
                "start_line": r[3],
                "end_line": r[4],
                "content": r[5]
            })
        return results

def main():
    rag = CodeRAG()
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python code_rag.py index <dir>    # Indexes code directory")
        print("  python code_rag.py search <query> # Searches codebase")
        return

    cmd = sys.argv[1]
    if cmd == "index":
        target = sys.argv[2] if len(sys.argv) > 2 else "."
        count = rag.index_directory(target)
        print(f"[SUCCESS] Indexed {count} code chunks.")
    elif cmd == "search":
        q = " ".join(sys.argv[2:])
        results = rag.search_code(q)
        print(f"\n--- Code Search Results for '{q}' ({len(results)} matches) ---")
        for res in results:
            print(f"\n📁 {res['file_path']} (Lines {res['start_line']}-{res['end_line']}) [{res['symbol_name']}]:")
            print("-" * 50)
            preview = "\n".join(res["content"].splitlines()[:10])
            print(preview)
            if len(res["content"].splitlines()) > 10:
                print("   ... [truncated] ...")

if __name__ == "__main__":
    main()
