import sys, os
import pytest
# Ensure the backend package root is on the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
from services.claim_extractor import extract_claims, _clean_claim_text, _split_compound_claims

@pytest.mark.asyncio
async def test_clean_markdown():
    md = """# Heading\n- Item 1\n- Item 2\n| Col | Val |\n|---|---|\n`code`\n**bold** text"""
    cleaned = _clean_claim_text(md)
    assert "Heading" not in cleaned
    assert "Item" in cleaned  # word remains after bullet removal
    assert "|" not in cleaned
    assert "code" not in cleaned
    assert "bold" in cleaned.lower()

@pytest.mark.asyncio
async def test_compound_splitting():
    text = "The system supports login; the system also supports logout."
    parts = _split_compound_claims(text)
    assert len(parts) == 2
    assert all(p.endswith('.') for p in parts)

@pytest.mark.asyncio
async def test_extraction_fallback_and_classification():
    response = "I think the sky is blue and it will rain tomorrow. Also, the current year is 2025."
    claims = await extract_claims(response)
    # Expect at least three claims: opinion, prediction, time-sensitive factual
    types = {c['type'] for c in claims}
    assert "opinion" in types
    assert "prediction" in types
    assert "time_sensitive_factual" in types

@pytest.mark.asyncio
async def test_duplicate_and_limit():
    # Create many similar claims to exceed limit
    repeated = "Water boils at 100°C. " * 20
    claims = await extract_claims(repeated)
    # Should de‑duplicate and cap at 10
    assert len(claims) <= 10
    texts = [c['text'] for c in claims]
    assert len(set(t.lower() for t in texts)) == len(claims)

