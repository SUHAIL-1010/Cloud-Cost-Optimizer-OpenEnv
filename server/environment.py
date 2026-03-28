# server/environment.py
from openenv.core.env_server import Environment
from models import CloudCostAction, CloudCostObservation, CloudCostState

class CloudCostEnvironment(Environment):
    def __init__(self, task_name="easy_cost_cut"):
        super().__init__()
        self.task_name = task_name
        self.servers = [{"id": "srv-1", "cpu": 5, "crit": False}, {"id": "db-1", "cpu": 80, "crit": True}]
        self.current_idx = 0
        self._state = CloudCostState(total_servers=len(self.servers))

    def reset(self) -> CloudCostObservation:
        self.current_idx = 0
        self._state = CloudCostState(total_servers=len(self.servers))
        return self._get_obs(reward=0.0, done=False)

    def _get_obs(self, reward=0.0, done=False) -> CloudCostObservation:
        if self.current_idx >= len(self.servers):
            return CloudCostObservation(server_id="DONE", cpu_usage=0, is_critical=False, remaining=0, reward=reward, done=True)
        
        srv = self.servers[self.current_idx]
        return CloudCostObservation(
            server_id=srv["id"], 
            cpu_usage=srv["cpu"], 
            is_critical=srv["crit"], 
            remaining=len(self.servers) - self.current_idx,
            reward=reward,
            done=done
        )

    def step(self, action: CloudCostAction) -> CloudCostObservation:
        if self.current_idx >= len(self.servers):
            return self._get_obs(reward=0.0, done=True)

        srv = self.servers[self.current_idx]
        reward = 0.0

        if action.decision == "terminate" and srv["crit"]:
            reward = -1.0
            self._state.penalties += 1
        elif action.decision == "terminate" and srv["cpu"] < 10:
            reward = 1.0
            self._state.money_saved += 1.0

        self.current_idx += 1
        done = self.current_idx >= len(self.servers)
        
        # Notice we are just returning the Observation now! No StepResult needed.
        return self._get_obs(reward=reward, done=done)

    @property
    def state(self) -> CloudCostState:
        return self._state