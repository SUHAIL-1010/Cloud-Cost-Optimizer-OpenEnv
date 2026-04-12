from pydantic import BaseModel

class CloudCostAction(BaseModel):
    server_id: str
    decision: str

class CloudCostObservation(BaseModel):
    server_id: str
    cluster_name: str
    node_capacity: int             # Traffic capacity of this specific node
    current_cpu_usage: float       # Dynamically calculated!
    memory_usage: int
    cluster_active_nodes: int      # How many servers are left in this cluster
    cluster_total_traffic: float   # The total load the cluster is handling
    is_critical_db: bool
    hourly_cost: float
    remaining: int
    reward: float = 0.0
    done: bool = False

class CloudCostState(BaseModel):
    total_servers: int
    money_saved: float
    outages_caused: int
    max_possible_savings: float
    success: bool