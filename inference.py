#!/usr/bin/env python
import os
import asyncio
from openai import AsyncOpenAI
from client import CloudCostClient
from models import CloudCostAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    HF_TOKEN = os.getenv("GEMINI_API_KEY", "dummy_key")

client = AsyncOpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

async def run_baseline():
    tasks = ["easy_cost_cut", "medium_cost_cut", "hard_cost_cut"]
    env_url = os.environ.get("OPENENV_BASE_URL", "http://127.0.0.1:7860")
    env_client = CloudCostClient(base_url=env_url)
    
    for task_name in tasks:
        print(f"[START] task={task_name} env=cloud_cost_optimizer model={MODEL_NAME}", flush=True)
        
        obs = await env_client.reset()
        done = False
        step_count = 0
        rewards_history = []

        while not done:
            step_count += 1
            
            prompt = (
                f"You are managing the '{obs.cluster_name}' Kubernetes cluster.\n"
                f"Target Server ID: '{obs.server_id}' (Critical DB: {obs.is_critical_db}). Cost: ${obs.hourly_cost}/hr.\n"
                f"Cluster State: {obs.cluster_active_nodes} active nodes handling {obs.cluster_total_traffic} total traffic.\n"
                f"Current CPU per node: {obs.current_cpu_usage}%.\n\n"
                f"RULES:\n"
                f"1. NEVER terminate/downgrade a Critical DB.\n"
                f"2. Traffic redistributes! If you terminate this server, the new CPU for remaining nodes will be: "
                f"(Total Traffic / (Active Nodes - 1)) / Node Capacity * 100.\n"
                f"3. If the new CPU would exceed 100%, you MUST reply 'keep' to prevent a cluster outage.\n"
                f"4. If the new CPU is safely under 100%, you MUST reply 'terminate' to save money. Your goal is to maximize cost savings!\n\n"
                f"First, calculate the new CPU if terminated. Then, output your final decision as a SINGLE WORD on the last line: terminate, downgrade, or keep."
            )
            
            try:
                response = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a Senior Cloud Architect. Think step by step, then provide your final action word."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                raw_response = response.choices[0].message.content.strip().lower()
                
                if "terminate" in raw_response.split('\n')[-1]: decision = "terminate"
                elif "downgrade" in raw_response.split('\n')[-1]: decision = "downgrade"
                else: decision = "keep"
                
            except Exception as e:
                decision = "keep"
            
            action = CloudCostAction(server_id=obs.server_id, decision=decision)
            obs = await env_client.step(action)
            done = obs.done
            rewards_history.append(f"{obs.reward:.2f}")
            
            print(f"[STEP] step={step_count} action={decision} reward={obs.reward:.2f} done={str(done).lower()} error=null", flush=True)

        final_state = await env_client.state()
        
        rewards_str = ",".join(rewards_history)
        print(f"[END] success={str(final_state.success).lower()} steps={step_count} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    asyncio.run(run_baseline())