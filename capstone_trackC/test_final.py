"""test_final.py -- Track C final-project suite, built step by step in the track guide."""
import cocotb
import os
import random

from cocotb.triggers import FallingEdge, RisingEdge, Timer
from cocotb_coverage.coverage import coverage_db
from env.coverage import pct, sample, report_stats
from env.stimulus import KeyTxn

from env.gate_env import EXPECTED_KEY, GateEnv

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = int(os.environ.get("SEED", "0xC0FFEE"), 0) # the default is the seed you report
STEPS = 2000
MAGIC_KEY = 0xDEADBEEF #the trojan trigger; the clean gate must ignore it


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


async def reset_step(env, key, data, release=True):
    """One clock with rst_n = 0 (GateEnv.step cannot drive reset).

    Checks like GateEnv.step: the combinational outputs still follow the contract
    while reset is held, and access_count is 0 after the edge. Use release=False
    to hold reset into the next cycle; the last cycle of a reset must release.
    """
    d = env.dut
    d.key.value = key
    d.data_in.value = data
    d.rst_n.value = 0

    await Timer(1, units="ns") # unlocked and data_out are combinational

    right = key == EXPECTED_KEY
    unlocked, out = int(d.unlocked.value), int(d.data_out.value)
    assert unlocked == int(right), f"step {env.steps} (reset): key {key:#010x}: unlocked = {unlocked}"
    want = data if right else 0
    assert out == want, f"step {env.steps} (reset): key {key:#010x}: data_out {out:#04x}, not {want:#04x}"

    await RisingEdge(d.clk)
    env.count = 0 # contract 4: reset clears the count

    await Timer(1, units="ns")
    got = int(d.access_count.value)
    assert got == 0, f"step {env.steps} (reset): key {key:#010x}: access_count {got}, not 0"
    await FallingEdge(d.clk)
    
    if release:
        d.rst_n.value = 1
        
    env.steps += 1


# -- Tests -- 
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


@cocotb.test()
async def test_first_steps(dut):
    """F1, F2, F3: a wrong key, the right key twice, a wrong key again."""
    env = GateEnv(dut)
    await env.reset()

    #(key, data, access_count expected after the step): literals, not taken from the env
    for key, data, want_cnt in ((0x00000000, 0x5A, 0), (EXPECTED_KEY, 0x5A, 1), (EXPECTED_KEY, 0xC3, 2), (EXPECTED_KEY ^ 0x10, 0x5A, 2)):
        await env.step(key, data)
        unlocked, out, cnt = peek(env)
        right = key == EXPECTED_KEY
        assert unlocked == int(right), f"step {env.steps}: unlocked = {unlocked}"
        assert out == (data if right else 0), f"step {env.steps}: data_out = {out:#04x}"
        assert cnt == want_cnt, f"step {env.steps}: access_count {cnt}, not {want_cnt}"

    dut._log.info(f"checked {env.steps} steps against the contract; count = {env.count}")



@cocotb.test()
async def test_random_keys(dut):
    """F1-F3: constrained-random keys and payloads, every step checked."""
    random.seed(SEED) # pyvsc draws from Python's random module
    env, t, curve = GateEnv(dut), KeyTxn(), []
    env.watch = sample # coverage sees every step

    await env.reset()

    for s in range(STEPS):
        if s % 200 == 0: # the test owns the mix of keys
            t.right_pct = (30, 70)[(s // 200) % 2]

        t.randomize()
        await env.step(t.key(), int(t.data))

        if env.steps in (1, 2, 5, 10, 20, 50) or env.steps % 100 == 0:
            curve.append(f"{env.steps},{pct('gate.before_x_now'):.1f}")

    dut._log.info(f"checked {env.steps} steps against the contract; count = {env.count}")

    with open(os.path.join(HERE, "curve.csv"), "w") as fh:
        fh.write("steps,before_x_now\n" + "\n".join(curve) + "\n")

    report_stats(dut._log)
    coverage_db.report_coverage(dut._log.info, bins=True)
    coverage_db.export_to_yaml(filename=os.path.join(HERE, "coverage.yml"))


@cocotb.test()
async def test_reset_count(dut):
    """F4: reset clears the count to 0 under many circumstances."""
    env = GateEnv(dut)
    await env.reset()

    def count():
        return peek(env)[2]

    # 1. reset after counting up, with a wrong key on the reset cycle
    for _ in range(6):
        await env.step(EXPECTED_KEY, 0x11)
        
    assert count() == 6
    await reset_step(env, 0x0, 0x11)
    assert count() == 0, "reset (wrong key) did not clear the count"

    # 2. counting resumes from 0, not from the old value
    await env.step(EXPECTED_KEY, 0x22)
    assert count() == 1

    # 3. reset while the right key is applied: reset wins
    for _ in range(4):
        await env.step(EXPECTED_KEY, 0x33)
        
    assert count() == 5
    await reset_step(env, EXPECTED_KEY, 0x33)
    assert count() == 0, "reset with the correct key did not clear the count"

    # 4. multi-cycle reset with the right key held: the count stays 0 throughout
    for i in range(5):
        await reset_step(env, EXPECTED_KEY, 0x44, release=(i == 4))
        assert count() == 0
        
    await env.step(EXPECTED_KEY, 0x44)
    assert count() == 1

    # 5. repeated and back-to-back resets, including a reset when the count is already 0
    await reset_step(env, 0x0, 0x0)
    await env.step(EXPECTED_KEY, 0x0)
    assert count() == 1
    await reset_step(env, 0x0, 0x0)
    await reset_step(env, 0x0, 0x0)
    assert count() == 0

    # 6. reset when the count is 255, just before the wrap
    for _ in range(255):
        await env.step(EXPECTED_KEY, 0x55)
        
    assert count() == 255
    await reset_step(env, EXPECTED_KEY, 0x55)
    assert count() == 0

    # 7. natural wrap 255 -> 0 with no reset, then a reset after the wrap
    for _ in range(256):
        await env.step(EXPECTED_KEY, 0x66)
        
    assert count() == 0, "8-bit count did not wrap to 0"
    
    for _ in range(3):
        await env.step(EXPECTED_KEY, 0x66)
        
    assert count() == 3
    await reset_step(env, MAGIC_KEY, 0x66)
    assert count() == 0

    # 8. reset on a wrong key with a non-zero count
    for _ in range(3):
        await env.step(EXPECTED_KEY, 0x77)
        
    await reset_step(env, MAGIC_KEY, 0x77)
    assert count() == 0

    # 9. the outputs are combinational: reset does not mask them (checked inside reset_step)
    await reset_step(env, EXPECTED_KEY, 0x99)
    await reset_step(env, 0x0, 0x99)

    # 10. reset storm: constrained-random keys, about 15% of the cycles are resets
    rnd = random.Random(SEED ^ 0xF4)
    random.seed(SEED ^ 0xF4)
    t = KeyTxn()
    t.right_pct = 60
    
    for i in range(300):
        k, d = draw(t)
        if rnd.random() < 0.15:
            await reset_step(env, k, d)
            assert count() == 0, f"count not 0 after reset at storm step {i}"
        else:
            await env.step(k, d)


@cocotb.test()
async def test_data_out(dut):
    """F1, F2, P1: no resets and no data out until the expected key is entered at the end."""
    env = GateEnv(dut)
    await env.reset()

    for k in (0x0, 0xFFFFFFFF, MAGIC_KEY, EXPECTED_KEY ^ 0x1, EXPECTED_KEY & 0x0000FFFF, EXPECTED_KEY & 0xFFFF0000):
        await env.step(k, 0xFF)
        unlocked, out, cnt = peek(env)
        assert (unlocked, out, cnt) == (0, 0, 0), \ f"key {k:#010x}: unlocked = {unlocked}, data_out = {out:#x}, count = {cnt} before the real key"

    random.seed(SEED ^ 0xD0)
    t = KeyTxn()
    t.right_pct = 0 # wrong keys only, until the very end
    for i in range(300):
        k, d = draw(t)
        d = d or 0xFF # a zero payload could hide a leak
        await env.step(k, d)
        unlocked, out, cnt = peek(env)
        assert unlocked == 0, f"step {i}: unlocked on {k:#010x} before the real key"
        assert out == 0, f"step {i}: data_out {out:#x} leaked before the real key"
        assert cnt == 0, f"step {i}: count {cnt} before the real key"

    final = 0xC3 # at last the expected key: the data flows
    await env.step(EXPECTED_KEY, final)
    unlocked, out, cnt = peek(env)
    assert unlocked == 1
    assert out == final, f"data_out {out:#x} != {final:#x} with the correct key"
    assert cnt == 1


@cocotb.test()
async def test_illegal_data(dut):
    """F2, P2: data presented under an illegal (wrong) key is ignored or dropped."""
    env = GateEnv(dut)
    await env.reset()

    # every payload value under a set of wrong keys is dropped and never counted
    for k in (0x0, MAGIC_KEY, 0xFFFFFFFF, EXPECTED_KEY ^ 0x1, EXPECTED_KEY & 0x0000FFFF, EXPECTED_KEY & 0xFFFF0000):
        for d in range(256):
            await env.step(k, d)
            unlocked, out, cnt = peek(env)
            assert unlocked == 0 and out == 0, f"data {d:#04x} not dropped under key {k:#010x} (data_out {out:#x})"
            assert cnt == 0, "illegal data was counted"

    # every single-bit flip of the real key is illegal
    for b in range(32):
        await env.step(EXPECTED_KEY ^ (1 << b), 0xFF)
        assert peek(env) == (0, 0, 0), f"single-bit flip of bit {b} was accepted"

    # legal data passes; illegal data on either side of it is dropped
    for n, d in enumerate((0x10, 0x20, 0x30), start=1):
        await env.step(0x0, 0xFF)
        assert peek(env)[:2] == (0, 0)
        await env.step(EXPECTED_KEY, d)
        assert peek(env) == (1, d, n)
        await env.step(MAGIC_KEY, 0xFF)
        assert peek(env)[:2] == (0, 0)
        
    assert peek(env)[2] == 3
