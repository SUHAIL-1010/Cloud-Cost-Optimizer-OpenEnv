from openenv.core import EnvClient
from models import CloudCostAction, CloudCostObservation, CloudCostState

class CloudCostClient(EnvClient[CloudCostAction, CloudCostObservation, CloudCostState]):
    def _step_payload(self, action: CloudCostAction) -> dict:
        return {"server_id": action.server_id, "decision": action.decision}

    def _parse_result(self, payload: dict) -> CloudCostObservation:
        # 1. Extract the actual observation data from the server's envelope
        obs_data = payload.get("observation", payload)
        
        # 2. Attach the reward and done flags so the Pydantic model is happy
        obs_data["reward"] = payload.get("reward", 0.0)
        obs_data["done"] = payload.get("done", False)
        
        return CloudCostObservation(**obs_data)

    def _parse_state(self, payload: dict) -> CloudCostState:
        return CloudCostState(**payload)