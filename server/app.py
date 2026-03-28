# server/app.py
from fastapi.responses import RedirectResponse
from openenv.core.env_server import create_fastapi_app
from models import CloudCostAction, CloudCostObservation
from server.environment import CloudCostEnvironment

app = create_fastapi_app(
    env=CloudCostEnvironment, 
    action_cls=CloudCostAction, 
    observation_cls=CloudCostObservation
)

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")
