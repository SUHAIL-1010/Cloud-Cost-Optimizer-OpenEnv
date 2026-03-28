import os
import asyncio
from openai import AsyncOpenAI  # 1. We import the Async client!
from client import CloudCostClient
from models import CloudCostAction

# 2. We use AsyncOpenAI
client = AsyncOpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

async def run_baseline():
    print("Connecting to environment...")
    env_client = CloudCostClient(base_url="http://127.0.0.1:8000")
    
    obs = await env_client.reset()
    done = False
    print(f"Started! First server to review: {obs.server_id}")

    while not done:
        prompt = (
            f"Server '{obs.server_id}' has {obs.cpu_usage}% CPU usage. "
            f"Is it a critical database? {obs.is_critical}. "
            f"Reply ONLY with one exact word: 'terminate', 'downgrade', or 'keep'."
        )
        
        # 3. We AWAIT the AI, so the script keeps breathing while it waits!
        response = await client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        decision = response.choices[0].message.content.strip().lower()
        if decision not in ["terminate", "downgrade", "keep"]: 
            decision = "keep"
        
        action = CloudCostAction(server_id=obs.server_id, decision=decision)
        
        # 4. Take the action and update our observation
        obs = await env_client.step(action)
        done = obs.done
        
        print(f"AI Action: {decision.upper()} | Reward: {obs.reward}")

    final_state = await env_client.state()
    print("\n--- TASK FINISHED ---")
    print(f"Total Servers Checked: {final_state.total_servers}")
    print(f"Money Saved: ${final_state.money_saved}")
    print(f"Critical Databases Terminated (Penalties): {final_state.penalties}")

if __name__ == "__main__":
    asyncio.run(run_baseline())
