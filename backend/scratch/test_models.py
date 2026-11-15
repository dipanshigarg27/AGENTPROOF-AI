import sys
import os
import asyncio

# Ensure the backend root is on the path so we can import the services package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from the backend .env file (absolute path based on this script)
from dotenv import load_dotenv
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(env_path)

# Verify that the Groq API key is present before proceeding
if not os.getenv('GROQ_API_KEY'):
    raise RuntimeError('GROQ_API_KEY not found in the environment. Please check backend/.env')

from services.bifrost_service import call_model, _get_client_for_model

async def main():
    task = "Explain the purpose of AgentProof AI in one sentence."
    model_ids = ["openai/gpt-oss-120b"]
    for model_id in model_ids:
        # Determine provider without Bifrost (force direct fallback)
        client, _ = _get_client_for_model(model_id, use_bifrost=False)
        base_url = getattr(client, "base_url", "")
        provider_name = "groq" if "groq.com" in str(base_url) else "openai"
        print(f"Provider resolved: {provider_name} (base_url={base_url})")
        print(f"\nCalling model {model_id} ...")
        result = await call_model(model_id, task, max_tokens=200)
        print("Response text:")
        print(result.get("response_text"))
        print(f"Latency (ms): {result.get('latency_ms')}")
        print(f"Prompt tokens: {result.get('prompt_tokens')}, Completion tokens: {result.get('completion_tokens')}, Total tokens: {result.get('total_tokens')}")
        print(f"Estimated cost USD: {result.get('estimated_cost_usd')}")
        if result.get('error'):
            print(f"API error: {result.get('error')}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
