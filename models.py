from openenv.core.env_server import Action, Observation, State

class CloudCostAction(Action):
    server_id: str
    decision: str 

class CloudCostObservation(Observation):
    hourly_cost: float
    server_id: str
    cpu_usage: int
    is_critical: bool
    remaining: int
    reward: float = 0.0  # ADD THIS
    done: bool = False   # ADD THIS

class CloudCostState(State):
    total_servers: int = 0
    money_saved: float = 0.0
    penalties: int = 0