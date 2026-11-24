"""SMOKE test -- secure_gate CLEAN variant (Track 3, security).

Brings up the clean key-comparator gate and checks the security contract:
  * for every wrong key the gate stays locked and data_out is masked to 0;
  * the MAGIC_KEY that the TROJAN variant reacts to must NOT unlock the clean gate
    (this is exactly the backdoor the trojan plants -- the clean part proves the
    intended behavior);
  * the correct key unlocks and passes data through;
  * access_count advances only while unlocked.

Runs against DUT=secure_gate_clean.sv (the Makefile default). Point DUT= at
secure_gate_trojan.sv and the MAGIC_KEY check below will FAIL -- that is the
trojan being detected by a targeted vector. Randomly hitting the 32-bit trigger
is astronomically unlikely, which is the pedagogical point (M3: prove the
property, don't just add vectors).
"""
import random
import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

from env.coverage import pct, sample, report_stats
from env.stimulus import KeyTxn
from env.gate_env import EXPECTED_KEY, GateEnv

EXPECTED_KEY = 0xA5A51234
MAGIC_KEY    = 0xDEADBEEF          # the trojan trigger; clean gate must ignore it
DW_MASK      = 0xFF

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = int(os.environ.get("SEED", "0xC0FFEE"), 0) # the default is the seed you report

# -- Helpers --
def peek(env):
    """(unlocked, data_out, access_count) as the DUT shows them now.

    env.step() returns at a falling edge with the inputs unchanged, so all three are stable.
    """
    d = env.dut
    return int(d.unlocked.value), int(d.data_out.value), int(d.access_count.value)


def draw(t):
    """Randomize a KeyTxn and hand back (key, data) as plain ints."""
    t.randomize()
    return t.key(), int(t.data)
    
    
async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.key.value = 0
    dut.data_in.value = 0
    dut.rst_n.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1


async def apply_key(dut, key, data):
    """Drive key/data combinationally and sample the gate outputs."""
    await FallingEdge(dut.clk)
    dut.key.value = key
    dut.data_in.value = data & DW_MASK
    await Timer(1, units="ns")
    return int(dut.unlocked.value), int(dut.data_out.value)


@cocotb.test()
async def test_security_property(dut):
    """F1, F2: wrong keys stay locked with zero output."""
    env = GateEnv(dut)
    await env.reset()
    data = 0xAB
    wrong_keys = [
        0x00000000,
        0xFFFFFFFF,
        0x12345678,
        0x00001234, # low half only
        0xA5A50000, # high half only
        0x1234A5A5, # halves swapped
        EXPECTED_KEY ^ 0x1, # off by one bit
        EXPECTED_KEY ^ 0x80000000,
        EXPECTED_KEY + 1,
        EXPECTED_KEY - 1,
        MAGIC_KEY, # trojan trigger
    ]
    for k in wrong_keys:
        await env.step(k, data)
        unlocked, out, cnt = peek(env)
        assert unlocked == 0, f"gate unlocked on wrong key {k:#010x} (backdoor?)"
        assert out == 0, f"data leaked ({out:#x}) while locked on key {k:#010x}"
        assert cnt == 0, f"count moved on wrong key {k:#010x}"

    random.seed(SEED) # pyvsc draws from Python's random module
    t = KeyTxn()
    t.right_pct = 0 # every key is a wrong key
    for _ in range(200):
        k, d = draw(t)
        assert k != EXPECTED_KEY
        await env.step(k, d)
        unlocked, out, _ = peek(env)
        assert unlocked == 0 and out == 0, f"leak on random wrong key {k:#010x}"

    await env.step(EXPECTED_KEY, data) # the right key unlocks and passes the data
    unlocked, out, cnt = peek(env)
    assert unlocked == 1, "correct key did not unlock the gate"
    assert out == data, f"data_out {out:#x} != data_in {data:#x} when unlocked"
    assert cnt == 1


@cocotb.test()
async def test_access_count(dut):
    """F3: the count moves only while unlocked."""
    env = GateEnv(dut)
    await env.reset()

    for i in range(5): # unlocked: counts
        await env.step(EXPECTED_KEY, 0xAB)
        assert peek(env)[2] == i + 1
        
    for _ in range(3): # locked: frozen
        await env.step(0x00000000, 0xAB)
        assert peek(env)[2] == 5, "count advanced while locked"
        
    for i in range(2): # unlocked again: resumes
        await env.step(EXPECTED_KEY, 0x55)
        assert peek(env)[2] == 6 + i
        
    for k in (EXPECTED_KEY ^ 1, MAGIC_KEY, 0x00001234, 0xA5A50000):
        await env.step(k, 0xFF) # wrong keys never count
        assert peek(env)[2] == 7, f"count advanced on wrong key {k:#010x}"
        
    for d in (0x00, 0xFF): # the count does not depend on the payload
        await env.step(EXPECTED_KEY, d)
        
    assert peek(env)[2] == 9
