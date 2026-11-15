import os, json, time, subprocess, sys
import urllib.request

BASE_URL = 'http://127.0.0.1:8000'

payload = {
    "task": "Explain AgentProof AI in one sentence.",
    "model_ids": ["openai/gpt-oss-120b", "openai/gpt-oss-safeguard-20b"],
    "max_tokens": 200,
}

# POST evaluation request via curl
post_cmd = [
    'curl', '-s', '-X', 'POST', f"{BASE_URL}/api/evaluations",
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(payload)
]
result = subprocess.check_output(post_cmd).decode()
resp = json.loads(result)

evaluation_id = resp.get('evaluation_id')
print('Evaluation ID:', evaluation_id)

# poll DB for status
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('database', os.path.join(os.path.dirname(__file__), '..', 'database.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
DB_PATH = mod.DB_PATH
import aiosqlite, asyncio

async def poll_status(eid, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('SELECT status FROM evaluations WHERE id = ?', (eid,)) as cur:
                row = await cur.fetchone()
                if row and row[0] in ('completed', 'failed'):
                    return row[0]
        await asyncio.sleep(2)
    return None

status = asyncio.run(poll_status(evaluation_id))
print('Final status:', status)

if status == 'completed':
    # fetch report via curl
    report_cmd = ['curl', '-s', f"{BASE_URL}/api/evaluations/{evaluation_id}/report"]
    report = subprocess.check_output(report_cmd).decode()
    print('Report:', report)
else:
    print('Evaluation did not complete')

