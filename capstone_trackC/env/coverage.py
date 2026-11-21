"""env/coverage.py -- functional coverage for secure_gate (cocotb-coverage)."""
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from env.gate_env import EXPECTED_KEY

STATE = ["unlocked", "locked"]
last = {"key": 0} # the key from the cycle before

@CoverPoint("gate.now", xf=lambda key, before: key == EXPECTED_KEY, bins=[True, False], bins_labels=STATE)

@CoverPoint("gate.before", xf=lambda key, before: before == EXPECTED_KEY, bins=[True, False], bins_labels=STATE)

@CoverCross("gate.before_x_now", items=["gate.before", "gate.now"])
def sample_step(key, before):
    """Every step: was the gate open on the cycle before, and is it open now?"""

def sample(key, data, count):
    """The env calls this every step, before the edge."""
    sample_step(key, last["key"])
    last["key"] = key

def pct(name):
    return coverage_db[name].cover_percentage
