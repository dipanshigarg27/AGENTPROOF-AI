import os, sys, time, json, asyncio
import aiosqlite
import subprocess

# Get DB path from backend/database.py
spec_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.py'))
import importlib.util
spec = importlib.util.spec_from_file_location('database', spec_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
DB_PATH = mod.DB_PATH

eval_id = 'b63898fa-167d-49d2-aef2-5edc1326e97b'

async def get_status():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT status FROM evaluations WHERE id = ?', (eval_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None

def fetch_report():
    url = f'http://127.0.0.1:8000/api/evaluations/{eval_id}/report'
    try:
        out = subprocess.check_output(['curl', '-s', url]).decode()
        return out
    except Exception as e:
        return str(e)

async def main():
    print('Polling evaluation', eval_id)
    for _ in range(90):  # up to 3 minutes
        status = await get_status()
        print('Current status:', status)
        if status in ('completed', 'failed'):
            break
        await asyncio.sleep(2)
    else:
        print('Timeout waiting for evaluation to finish')
        sys.exit(1)
    print('Fetching report...')
    report = fetch_report()
    print('REPORT_START')
    print(report)
    print('REPORT_END')

if __name__ == '__main__':
    asyncio.run(main())

