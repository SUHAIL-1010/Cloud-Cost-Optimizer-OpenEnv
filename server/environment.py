import random
from openenv.core.env_server import Environment
from models import CloudCostAction, CloudCostObservation, CloudCostState

class CloudCostEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self.reset_simulation()

    def reset_simulation(self):
        # Initialize 3 distinct Kubernetes Clusters with live traffic loads
        self.clusters = {
            "Frontend-Web": {"traffic": 350.0, "nodes": 5, "capacity_per_node": 100},
            "Backend-API": {"traffic": 220.0, "nodes": 4, "capacity_per_node": 100},
            "Data-Processing": {"traffic": 80.0, "nodes": 3, "capacity_per_node": 100}
        }
        
        self.queue = []
        server_id_counter = 1
        
        # Populate the servers into the queue based on the clusters
        for cluster_name, data in self.clusters.items():
            for _ in range(data["nodes"]):
                self.queue.append({
                    "id": f"srv-{server_id_counter}",
                    "cluster": cluster_name,
                    "is_critical": True if "Data" in cluster_name else False,
                    "hourly_cost": round(random.uniform(2.00, 8.00), 2),
                    "memory": random.randint(10, 90)
                })
                server_id_counter += 1
                
        # Shuffle the queue to make it unpredictable
        random.shuffle(self.queue)
        
        self.money_saved = 0.0
        self.outages = 0
        self.total_servers = len(self.queue)
        # Approximate perfection (terminating all safe redundancy)
        self.max_possible_savings = sum(s["hourly_cost"] for s in self.queue) * 0.4 

    def reset(self) -> CloudCostObservation:
        self.reset_simulation()
        return self._get_observation(reward=0.0, done=False)

    def _get_observation(self, reward: float, done: bool) -> CloudCostObservation:
        if not self.queue:
            return CloudCostObservation(
                server_id="DONE", cluster_name="NONE", node_capacity=0, current_cpu_usage=0.0,
                memory_usage=0, cluster_active_nodes=0, cluster_total_traffic=0.0,
                is_critical_db=False, hourly_cost=0.0, remaining=0, reward=reward, done=True
            )
            
        current = self.queue[0]
        c_name = current["cluster"]
        cluster_data = self.clusters[c_name]
        
        # DYNAMIC MATH: CPU is calculated in real-time based on active nodes
        current_cpu = (cluster_data["traffic"] / cluster_data["nodes"]) / cluster_data["capacity_per_node"] * 100

        return CloudCostObservation(
            server_id=current["id"],
            cluster_name=c_name,
            node_capacity=cluster_data["capacity_per_node"],
            current_cpu_usage=round(current_cpu, 1),
            memory_usage=current["memory"],
            cluster_active_nodes=cluster_data["nodes"],
            cluster_total_traffic=cluster_data["traffic"],
            is_critical_db=current["is_critical"],
            hourly_cost=current["hourly_cost"],
            remaining=len(self.queue),
            reward=reward,
            done=done
        )

    def step(self, action: CloudCostAction) -> CloudCostObservation:
        if not self.queue:
            return self._get_observation(reward=0.0, done=True)

        current = self.queue.pop(0)
        c_name = current["cluster"]
        cluster_data = self.clusters[c_name]
        reward = 0.0

        if action.decision == "terminate":
            if current["is_critical"]:
                reward = -10.0 # Catastrophic failure
                self.outages += 1
            else:
                # SIMULATE THE CONSEQUENCE: Traffic redistributes!
                simulated_nodes = cluster_data["nodes"] - 1
                if simulated_nodes == 0:
                    new_cpu = 999 # Complete cluster crash
                else:
                    new_cpu = (cluster_data["traffic"] / simulated_nodes) / cluster_data["capacity_per_node"] * 100
                
                if new_cpu > 100.0:
                    # AI caused an outage by overloading the remaining servers
                    reward = -5.0
                    self.outages += 1
                    # Do not actually terminate it, the system protected itself
                else:
                    # Success! Safe termination.
                    cluster_data["nodes"] -= 1 # Officially remove it from the cluster
                    reward = current["hourly_cost"]
                    self.money_saved += reward

        elif action.decision == "downgrade":
            if current["is_critical"]:
                reward = -2.0
            else:
                # Downgrading reduces the capacity of THIS node
                simulated_capacity = cluster_data["capacity_per_node"] * 0.5
                new_cpu = (cluster_data["traffic"] / cluster_data["nodes"]) / simulated_capacity * 100
                
                if new_cpu > 100.0:
                    reward = -2.0 # Cannot downgrade, load is too high
                else:
                    cluster_data["capacity_per_node"] = simulated_capacity
                    reward = current["hourly_cost"] * 0.5
                    self.money_saved += reward

        done = len(self.queue) == 0
        return self._get_observation(reward=round(reward, 2), done=done)

    @property
    def state(self) -> CloudCostState:
        return CloudCostState(
            total_servers=self.total_servers,
            money_saved=round(self.money_saved, 2),
            outages_caused=self.outages,
            max_possible_savings=round(self.max_possible_savings, 2),
            success=(self.outages == 0)
        )