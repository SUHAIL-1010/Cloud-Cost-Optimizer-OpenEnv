# server/app.py
from openenv.core.env_server import create_fastapi_app
from models import CloudCostAction, CloudCostObservation
from server.environment import CloudCostEnvironment

app = create_fastapi_app(
    env=CloudCostEnvironment, 
    action_cls=CloudCostAction, 
    observation_cls=CloudCostObservation
)

# Return a simple health check dictionary instead of a redirect!
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Environment is successfully running"}
