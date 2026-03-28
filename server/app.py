# server/app.py
from openenv.core.env_server import create_fastapi_app
from models import CloudCostAction, CloudCostObservation
from server.environment import CloudCostEnvironment

# We pass the class ITSELF (CloudCostEnvironment), no parentheses!
app = create_fastapi_app(
    env=CloudCostEnvironment, 
    action_cls=CloudCostAction, 
    observation_cls=CloudCostObservation
)