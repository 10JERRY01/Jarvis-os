"""
Jarvis Memory, Knowledge Indexer & Total Recall Engine
Handles Markdown notes, real-time live indexing, keyword/semantic retrieval,
and updates the 3D Knowledge Galaxy data dynamically.
"""

import os
import re
import json
import time
import sqlite3
import datetime
from typing import List, Dict, Any, Tuple

class MemoryEngine:
    def __init__(self, config: Dict[str, Any]):
        self.cfg = config.get("memory", {})
        self.notes_dir = os.path.abspath(self.cfg.get("notes_dir", "./notes"))
        self.captures_dir = os.path.abspath(self.cfg.get("captures_dir", "./notes/captures"))
        self.index_path = os.path.abspath(self.cfg.get("index_path", "./viewer/graph-data.js"))
        self.db_path = os.path.abspath(self.cfg.get("sqlite_db", "./memory/jarvis_memory.db"))
        self.top_k = self.cfg.get("top_k_retrieval", 6)

        os.makedirs(self.notes_dir, exist_ok=True)
        os.makedirs(self.captures_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        self._init_db()
        self.build_initial_graph_if_missing()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                title TEXT,
                path TEXT UNIQUE,
                excerpt TEXT,
                content TEXT,
                created_at TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
                title, content, content='notes', content_rowid='id'
            )
        """)
        conn.commit()
        conn.close()

    def remember(self, phrase: str) -> Dict[str, Any]:
        """
        Total Recall handler:
        Captures memory phrase, creates markdown note, updates index & graph-data.js.
        """
        cleaned = re.sub(r'^(remember that|note to self|remember|log this)\s*', '', phrase, flags=re.IGNORECASE).strip()
        if not cleaned:
            return {"success": False, "error": "Empty note content."}

        # Title from first 5-6 words
        words = cleaned.split()
        title_slug = "_".join(re.sub(r'[^a-zA-Z0-9]', '', w) for w in words[:5]) or "note"
        date_str = datetime.date.today().isoformat()
        filename = f"{date_str}_{title_slug}.md"
        filepath = os.path.join(self.captures_dir, filename)

        markdown_content = f"# {title_slug.replace('_', ' ').capitalize()}\nDate: {date_str}\n\n{cleaned}\n"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            # Insert into SQLite index
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO notes (title, path, excerpt, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (title_slug.replace('_', ' '), filepath, cleaned[:300], cleaned, datetime.datetime.now())
            )
            note_id = cur.lastrowid
            cur.execute(
                "INSERT INTO notes_fts (rowid, title, content) VALUES (?, ?, ?)",
                (note_id, title_slug.replace('_', ' '), cleaned)
            )
            conn.commit()
            conn.close()

            # Append to graph-data.js for live 3D galaxy render
            self._append_to_graph_js(note_id, title_slug.replace('_', ' '), cleaned[:300])

            return {
                "success": True,
                "note_id": note_id,
                "title": title_slug.replace('_', ' '),
                "path": filepath
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_notes(self, query: str) -> Tuple[str, List[int]]:
        """
        Retrieves top K relevant notes for a given question.
        Returns combined context text and list of note indexes.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Simple BM25 ranking via SQLite FTS5
        words = re.findall(r'\w+', query)
        if not words:
            conn.close()
            return "", []

        match_query = " OR ".join([f'"{w}"*' for w in words[:6]])
        try:
            cur.execute("""
                SELECT n.id, n.title, n.excerpt, n.content, rank
                FROM notes_fts(?) fts
                JOIN notes n ON n.id = fts.rowid
                ORDER BY rank
                LIMIT ?
            """, (match_query, self.top_k))
            rows = cur.fetchall()
        except Exception:
            rows = []

        conn.close()

        if not rows:
            return "", []

        context_snippets = []
        node_indexes = []
        for r in rows:
            node_indexes.append(r[0])
            context_snippets.append(f"### {r[1]}\n{r[3]}")

        return "\n\n".join(context_snippets), node_indexes

    def _append_to_graph_js(self, node_id: int, title: str, excerpt: str):
        """Updates graph-data.js with the newly born node."""
        if not os.path.exists(self.index_path):
            self.build_initial_graph_if_missing()
            return

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                content = f.read()

            match = re.search(r'const GRAPH = (\{.*?\});', content, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                new_node = {
                    "id": node_id,
                    "label": title,
                    "group": "captures",
                    "excerpt": excerpt
                }
                data["nodes"].append(new_node)
                # Link to nearest node or first node if available
                if len(data["nodes"]) > 1:
                    data["links"].append({"source": node_id, "target": data["nodes"][0]["id"]})

                with open(self.index_path, "w", encoding="utf-8") as f:
                    f.write(f"const GRAPH = {json.dumps(data, indent=2)};\n")
        except Exception:
            pass

    def build_initial_graph_if_missing(self):
        if os.path.exists(self.index_path):
            return

        sample_graph = {
            "nodes": [
                {"id": 0, "label": "Jarvis Operating System", "group": "system", "excerpt": "The native AI-first Linux OS for local ML and gaming."},
                {"id": 1, "label": "Local LLM Acceleration", "group": "ai", "excerpt": "Ollama and llama.cpp runtime bound to local ports."},
                {"id": 2, "label": "Kernel & Gaming", "group": "gaming", "excerpt": "BORE scheduler and Proton GE for ultra-low latency."}
            ],
            "links": [
                {"source": 0, "target": 1},
                {"source": 0, "target": 2}
            ]
        }
        with open(self.index_path, "w", encoding="utf-8") as f:
            f.write(f"const GRAPH = {json.dumps(sample_graph, indent=2)};\n")
