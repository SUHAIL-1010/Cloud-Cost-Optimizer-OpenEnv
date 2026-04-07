---
title: Cloud Cost Optimizer OpenEnv
emoji: ☁️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# ☁️ OpenEnv: Enterprise Cloud Cost Optimizer
**An RL Environment for High-Stakes Infrastructure Automation**

[![Live Demo](https://img.shields.io/badge/Live_Environment-Hugging_Face-blue?logo=huggingface)](https://huggingface.co/spaces/SuhaiL10102005/Cloud-Cost-Optimizer-OpenEnv)
[![Validation](https://img.shields.io/badge/OpenEnv-Compliant-success)](#)

## 📌 Architectural Motivation
Managing cloud infrastructure costs at scale is a critical, high-stakes operation. SREs and DevOps teams must continuously monitor metrics to terminate underutilized instances or downsize them. However, they must balance cost-cutting with **catastrophic risk mitigation**—ensuring critical production databases are never taken offline.

This environment simulates that exact paradigm, challenging an AI agent to optimize real-world AWS/GCP hourly costs dynamically without causing production outages.

## 🧠 The Agent Persona (System Prompting)
The baseline AI (`inference.py`) utilizes **Gemini 2.5 Flash** acting as a Senior SRE. 
* **Temperature: 0.0** -> Cost optimization requires strict deterministic logic, not creative hallucination. The temperature is zeroed to ensure maximum safety.
* **Fallback Mechanisms** -> The agent is wrapped in robust exception handling, automatically defaulting to `keep` (safe state) if API limits are hit, preventing catastrophic pipeline failures.

## 📊 Dynamic State & Observation Space
Each state step yields a localized `CloudCostObservation` mimicking a Datadog/CloudWatch alert:
* `server_id`: Instance UUID.
* `cpu_usage`: Live processing load (0-100%).
* `is_critical`: Boolean flag (protected database).
* `hourly_cost`: Dynamic floating-point dollar cost of the server (e.g., $4.25/hr).

## 🕹️ Action Space & Economic Reward Shaping
The environment employs **dynamic, economics-based reward shaping** rather than flat scalars:

| Action | Scenario | Reward / Penalty | Impact |
| :--- | :--- | :--- | :--- |
| `terminate` | Idle Server (CPU < 10%) | **+ (hourly_cost)** | Direct dollar savings. |
| `downgrade` | Underutilized (CPU < 40%) | **+ (hourly_cost / 2)** | Partial capacity efficiency. |
| `keep` | Busy / Critical Server | **0.0** | Baseline safety maintained. |
| `terminate` | **Critical Database** | **-5.0 (Penalty)** | Catastrophic data loss. Instantly ruins final score. |

## 🏆 Scoring Logic
The final deterministic grader returns a normalized score. Money saved is calculated, but **any** critical databases terminated will result in an immediate penalty flag, dropping the final deployment score to `0.0`. Safety supersedes savings.