"""env/gate_env.py -- driver, monitor, and scoreboard for secure_gate: the contract, every cycle."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

EXPECTED_KEY = 0xA5A51234 # SPEC.md, Parameters

class GateEnv:
    def __init__(self, dut):
    self.dut = dut
    self.count = 0 # the reference for access_count
    self.watch = None # coverage hook: watch(key, data, count)
    self.steps = 0
    async def reset(self):
    d = self.dut
    cocotb.start_soon(Clock(d.clk, 10, units="ns").start())
    d.key.value = 0
    d.data_in.value = 0
    d.rst_n.value = 0
    for _ in range(3):
    await RisingEdge(d.clk)
    await FallingEdge(d.clk)
    d.rst_n.value = 1
