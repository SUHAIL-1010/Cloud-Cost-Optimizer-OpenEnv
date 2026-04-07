import random
from openenv.core.env_server import Environment
from models import CloudCostAction, CloudCostObservation, CloudCostState

class CloudCostEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self._generate_queue()
        self.money_saved = 0.0
        self.penalties = 0
        self.total_servers = len(self.queue)
        self.servers_processed = 0

    def _generate_queue(self):
        # Generate a realistic queue of servers with random hourly costs
        self.queue = []
        for i in range(10):
            self.queue.append({
                "id": f"srv-{i+1}",
                "cpu": random.randint(0, 100),
                "is_critical": random.choice([True, False, False, False]), # 25% chance to be a DB
                "hourly_cost": round(random.uniform(0.50, 8.00), 2) # e.g., $0.50 to $8.00 per hour
            })

    # FIX: Removed 'async' from here
    def reset(self) -> CloudCostObservation:
        self._generate_queue()
        self.money_saved = 0.0
        self.penalties = 0
        self.total_servers = len(self.queue)
        self.servers_processed = 0
        return self._get_observation(reward=0.0, done=False)

    def _get_observation(self, reward: float, done: bool) -> CloudCostObservation:
        if not self.queue:
            return CloudCostObservation(
                server_id="DONE", cpu_usage=0, is_critical=False, hourly_cost=0.0,
                remaining=0, reward=reward, done=True
            )
        current = self.queue[0]
        return CloudCostObservation(
            server_id=current["id"],
            cpu_usage=current["cpu"],
            is_critical=current["is_critical"],
            hourly_cost=current["hourly_cost"],
            remaining=len(self.queue),
            reward=reward,
            done=done
        )

    # FIX: Removed 'async' from here
    def step(self, action: CloudCostAction) -> CloudCostObservation:
        if not self.queue:
            return self._get_observation(reward=0.0, done=True)

        current = self.queue.pop(0)
        self.servers_processed += 1
        reward = 0.0

        # Reward Logic based on real Cloud Economics
        if action.decision == "terminate":
            if current["is_critical"]:
                # Catastrophic failure: Database terminated
                reward = -5.0 
                self.penalties += 1
            elif current["cpu"] < 10:
                # Success: Terminated an idle server, save full hourly cost
                reward = current["hourly_cost"]
                self.money_saved += current["hourly_cost"]
            else:
                # Penalty: Terminated a busy server
                reward = -0.5 

        elif action.decision == "downgrade":
            if not current["is_critical"] and current["cpu"] < 40:
                # Success: Downgraded underutilized server, save half cost
                savings = current["hourly_cost"] / 2
                reward = savings
                self.money_saved += savings

        # Keeping a busy or critical server is safe/neutral (Reward = 0.0)

        done = len(self.queue) == 0
        return self._get_observation(reward=reward, done=done)

    # FIX: Removed 'async' from here
    def state(self) -> CloudCostState:
        return CloudCostState(
            total_servers=self.total_servers,
            servers_processed=self.servers_processed,
            money_saved=round(self.money_saved, 2),
            penalties=self.penalties
        )
# FIX: Added @property so the framework can read it!
    @property
    def state(self) -> CloudCostState:
        return CloudCostState(
            total_servers=self.total_servers,
            servers_processed=self.servers_processed,
            money_saved=round(self.money_saved, 2),
            penalties=self.penalties
        )