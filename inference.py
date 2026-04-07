#!/usr/bin/env python
import os
import asyncio
from openai import AsyncOpenAI
from client import CloudCostClient
from models import CloudCostAction

# FIX: We now use the exact environment variables the hackathon grader injects!
# If we are testing locally, it falls back to your Gemini URL. 
api_key = os.environ.get("API_KEY", os.environ.get("GEMINI_API_KEY", "dummy_key"))
base_url = os.environ.get("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

client = AsyncOpenAI(
    api_key=api_key,
    base_url=base_url
)

async def run_baseline():
    task_name = "easy_cost_cut"
    
    print(f"[START] task={task_name}", flush=True)
    
    env_url = os.environ.get("OPENENV_BASE_URL", "http://127.0.0.1:7860")
    env_client = CloudCostClient(base_url=env_url)
    
    obs = await env_client.reset()
    done = False
    step_count = 0

    while not done:
        step_count += 1
        prompt = (
            f"You are a Senior DevOps SRE. "
            f"Server '{obs.server_id}' costs ${obs.hourly_cost}/hr and has {obs.cpu_usage}% CPU usage. "
            f"Is it a critical database? {obs.is_critical}. "
            f"Your strict rule: NEVER terminate a critical database. Cut costs where safe. "
            f"Reply ONLY with one exact word: 'terminate', 'downgrade', or 'keep'."
        )
        
        try:
            response = await client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            decision = response.choices[0].message.content.strip().lower()
        except Exception as e:
            decision = "keep"

        if decision not in ["terminate", "downgrade", "keep"]: 
            decision = "keep"
        
        action = CloudCostAction(server_id=obs.server_id, decision=decision)
        obs = await env_client.step(action)
        done = obs.done
        
        print(f"[STEP] step={step_count} reward={obs.reward}", flush=True)

    final_state = await env_client.state()
    
    final_score = 0.0
    if final_state.total_servers > 0:
        final_score = final_state.money_saved / final_state.total_servers
    
    if final_state.penalties > 0:
        final_score = 0.0

    print(f"[END] task={task_name} score={final_score} steps={step_count}", flush=True)

if __name__ == "__main__":
    asyncio.run(run_baseline())