"""
AgentProof AI — SQLite Database
Schema creation and async helper functions using aiosqlite
"""
import aiosqlite
import logging
import os
from datetime import datetime

logger = logging.getLogger("agentproof.db")

# Resolve the SQLite database path robustly, independent of the current working directory.

def _resolve_db_path() -> str:
    """Return the absolute path to ``agentproof.db`` located alongside this file.
    This works even if the module is imported after a ``os.chdir`` call.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "agentproof.db")

# Public constant for backward compatibility.
DB_PATH = _resolve_db_path()



async def init_db():
    """Create all tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id TEXT PRIMARY KEY,
            task TEXT NOT NULL,
            task_category TEXT DEFAULT 'General Knowledge',
            custom_instructions TEXT,
            max_tokens INTEGER DEFAULT 1000,
            status TEXT DEFAULT 'pending',
            demo_mode INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS evaluation_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            display_name TEXT NOT NULL,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        );

        CREATE TABLE IF NOT EXISTS model_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            response_text TEXT,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            latency_ms REAL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            estimated_cost_usd REAL,
            finish_reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        );

        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            claim_text TEXT NOT NULL,
            claim_type TEXT NOT NULL,
            claim_index INTEGER NOT NULL,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        );

        CREATE TABLE IF NOT EXISTS verification_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            explanation TEXT,
            evidence_summary TEXT,
            retrieved_at TEXT NOT NULL,
            FOREIGN KEY (claim_id) REFERENCES claims(id)
        );

        CREATE TABLE IF NOT EXISTS evidence_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verification_id INTEGER NOT NULL,
            title TEXT,
            url TEXT NOT NULL,
            snippet TEXT,
            published_date TEXT,
            relevance_score REAL,
            FOREIGN KEY (verification_id) REFERENCES verification_results(id)
        );

        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            trust_score REAL,
            efficiency_score REAL,
            task_completion_score REAL,
            verified_claims INTEGER DEFAULT 0,
            contradicted_claims INTEGER DEFAULT 0,
            outdated_claims INTEGER DEFAULT 0,
            unverifiable_claims INTEGER DEFAULT 0,
            opinion_claims INTEGER DEFAULT 0,
            total_claims INTEGER DEFAULT 0,
            trust_score_explanation TEXT,
            efficiency_score_explanation TEXT,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
        );
        """)
        await db.commit()
    logger.info("Database schema initialized.")


async def get_db():
    """Context manager to get a DB connection."""
    return aiosqlite.connect(DB_PATH)
