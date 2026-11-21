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
        self.count = 0

    async def step(self, key, data):
        """One clock: drive a key and a payload, check the outputs, then the counter."""
        d = self.dut
        d.key.value = key
        d.data_in.value = data

        await Timer(1, units="ns") # unlocked and data_out are combinational

        right = key == EXPECTED_KEY # contract 1: unlock iff the key matches
        unlocked, out = int(d.unlocked.value), int(d.data_out.value)

        assert unlocked == int(right), f"step {self.steps}: key {key:#010x}: unlocked = {unlocked}"

        want = data if right else 0 # contract 2: pass the payload, or mask it

        assert out == want, (f"step {self.steps}: key {key:#010x}: " f"data_out {out:#04x}, not {want:#04x}")

        if self.watch: # monitor: tell coverage, before the edge
            self.watch(key, data, self.count)

        await RisingEdge(d.clk)

        if right: # contract 3: count the unlocked cycles
            self.count = (self.count + 1) % 256

        await Timer(1, units="ns")
        got = int(d.access_count.value)
        assert got == self.count, f"step {self.steps}: access_count {got}, not {self.count}"
        await FallingEdge(d.clk)
        self.steps += 1
