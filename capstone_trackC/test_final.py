"""test_final.py -- Track C final-project suite, built step by step in the track guide."""
import cocotb

from env.gate_env import EXPECTED_KEY, GateEnv

@cocotb.test()

async def test_first_steps(dut):
    """F1, F2, F3: a wrong key, the right key twice, a wrong key again."""
    env = GateEnv(dut)
    await env.reset()
    for key, data in ((0x00000000, 0x5A), (EXPECTED_KEY, 0x5A), (EXPECTED_KEY, 0xC3), (EXPECTED_KEY ^ 0x10, 0x5A)):
        await env.step(key, data)

    dut._log.info(f"checked {env.steps} steps against the contract; count = {env.count}")
