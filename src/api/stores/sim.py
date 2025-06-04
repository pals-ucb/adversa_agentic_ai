# Updated store/sim.py
from typing import Dict
from uuid import uuid4
from ..schemas.sim import SimState, SimStatus, SimStepDetail

class SimStore:
    def __init__(self):
        self._store: Dict[str, SimState] = {}

    def start_sim(self, sim_model_id: str, step_mode: bool) -> str:
        sim_id = str(uuid4())
        self._store[sim_id] = SimState(
            sim_id=sim_id,
            current_step=0,
            status=SimStatus.RUNNING,
            steps={}
        )
        return sim_id

    def get_state(self, sim_id: str) -> SimState:
        return self._store[sim_id]

    def add_step(self, sim_id: str, detail: SimStepDetail):
        sim = self._store[sim_id]
        sim.steps[detail.step_number] = detail
        sim.current_step = detail.step_number

    def complete(self, sim_id: str):
        self._store[sim_id].status = SimStatus.COMPLETED

    def fail(self, sim_id: str):
        self._store[sim_id].status = SimStatus.ERROR

