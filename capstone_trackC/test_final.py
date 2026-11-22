"""test_final.py -- Track C final-project suite, built step by step in the track guide."""
import cocotb
import os
import random

from cocotb_coverage.coverage import coverage_db
from env.coverage import pct, sample, report_stats
from env.stimulus import KeyTxn

from env.gate_env import EXPECTED_KEY, GateEnv

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = int(os.environ.get("SEED", "0xC0FFEE"), 0) # the default is the seed you report
STEPS = 2000

@cocotb.test()
async def test_first_steps(dut):
    """F1, F2, F3: a wrong key, the right key twice, a wrong key again."""
    env = GateEnv(dut)
    await env.reset()
    for key, data in ((0x00000000, 0x5A), (EXPECTED_KEY, 0x5A), (EXPECTED_KEY, 0xC3), (EXPECTED_KEY ^ 0x10, 0x5A)):
        await env.step(key, data)

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

