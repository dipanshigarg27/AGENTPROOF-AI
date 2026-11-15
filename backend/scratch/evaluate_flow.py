import os, sys, asyncio, time

# Ensure project root is on Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from main import app
from database import DB_PATH
import aiosqlite

client = TestClient(app)

async def wait_evaluation(evaluation_id: str, timeout: int = 180) -> str | None:
    """Poll the DB until the evaluation reaches a terminal state or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT status FROM evaluations WHERE id = ?", (evaluation_id,)) as cur:
                row = await cur.fetchone()
                if row and row[0] in ("completed", "failed"):
                    return row[0]
        await asyncio.sleep(2)
    return None

async def main():
    payload = {
        "task": "Explain AgentProof AI in one sentence.",
        "model_ids": ["openai/gpt-oss-120b", "openai/gpt-oss-safeguard-20b"],
        "max_tokens": 200,
    }
    # POST to the correct endpoint (prefix /api)
    response = client.post("/api/evaluations", json=payload)
    print("POST /api/evaluations status:", response.status_code)
    print(response.json())
    if response.status_code != 200:
        return
    evaluation_id = response.json()["evaluation_id"]
    final_status = await wait_evaluation(evaluation_id)
    print("Evaluation final status:", final_status)
    if final_status == "completed":
        report_resp = client.get(f"/api/evaluations/{evaluation_id}/report")
        print("GET /api/evaluations/{id}/report status:", report_resp.status_code)
        print(report_resp.json())
    else:
        print("Evaluation did not complete successfully.")

if __name__ == "__main__":
    asyncio.run(main())

