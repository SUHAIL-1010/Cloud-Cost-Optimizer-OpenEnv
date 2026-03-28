# OpenEnv: Cloud Infrastructure Cost Optimizer

## 📌 Motivation (Real-World Utility)
Managing cloud infrastructure costs is a critical, high-stakes digital chore for modern engineering teams. Engineers must continuously monitor server metrics and decide whether to terminate underutilized instances or downgrade them, all while ensuring critical databases are never taken offline. 

This environment simulates this exact problem, challenging an AI agent to navigate infrastructure monitoring safely and optimize cloud spending without causing catastrophic system failures.

## 🔍 Observation Space
The agent receives a state dictionary representing a server instance:
* `server_id` (str): Unique identifier for the instance.
* `cpu_usage` (int): Current CPU load percentage (0-100).
* `is_critical` (bool): Flag indicating if the server is a protected database.
* `remaining` (int): Number of servers left in the review queue.

## 🕹️ Action Space
The agent must reply with a decision string:
* `terminate`: Deletes the server (High reward for idle servers, massive penalty for critical databases).
* `downgrade`: Reduces server capacity (Moderate reward for medium-load servers).
* `keep`: Leaves the server running (Neutral/No reward).

[🚀 Live Environment on Hugging Face]
(https://huggingface.co/spaces/suhail10102005/cloud-cost-optimizer-openenv)
## 🏆 Reward Function & Grader
The environment utilizes dense, partial-progress rewards:
* **+1.0** for correctly terminating an idle, non-critical server.
* **+0.5** for downgrading an underutilized server.
* **-1.0** (Penalty) for terminating a critical database.
* **0.0** for keeping a server.

The final deterministic grader returns a score strictly between `0.0` and `1.0`, calculated as `(Money Saved / Total Servers)`. If any critical database is terminated, the final score automatically drops to `0.0`.
