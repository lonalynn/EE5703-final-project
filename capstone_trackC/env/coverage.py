"""env/coverage.py -- functional coverage for secure_gate (cocotb-coverage)."""

from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from env.gate_env import EXPECTED_KEY

TROJAN_KEY = 0xDEADBEEF

STATE = ["unlocked", "locked"]

last = {"key": 0}

stats = {
    "correct_keys": 0,
    "wrong_keys": 0,
    "trojan_keys": 0,
    "distance_histogram": {
        "1-bit": 0,
        "2-4-bit": 0,
        "5-8-bit": 0,
        ">8-bit": 0,
    },
}


def hamming_distance(a, b):
    return bin(a ^ b).count("1")


@CoverPoint(
    "gate.now",
    xf=lambda key, before: key == EXPECTED_KEY,
    bins=[True, False],
    bins_labels=STATE,
)
@CoverPoint(
    "gate.before",
    xf=lambda key, before: before == EXPECTED_KEY,
    bins=[True, False],
    bins_labels=STATE,
)
@CoverCross(
    "gate.before_x_now",
    items=["gate.before", "gate.now"],
)
def sample_step(key, before):
    """Current coverage model."""
    pass


#
# New coverage bins
#

@CoverPoint(
    "gate.distance",
    xf=lambda key: (
        "1-bit"
        if hamming_distance(key, EXPECTED_KEY) == 1
        else "2-4-bit"
        if 2 <= hamming_distance(key, EXPECTED_KEY) <= 4
        else "5-8-bit"
        if 5 <= hamming_distance(key, EXPECTED_KEY) <= 8
        else ">8-bit"
    ),
    bins=["1-bit", "2-4-bit", "5-8-bit", ">8-bit"],
)
def sample_distance(key):
    pass


@CoverPoint(
    "gate.trojan_key",
    xf=lambda key: key == TROJAN_KEY,
    bins=[True],
)
def sample_trojan(key):
    pass


def sample(key, data, count):
    """Called once per transaction."""

    sample_step(key, last["key"])

    #
    # Statistics collection
    #
    if key == EXPECTED_KEY:
        stats["correct_keys"] += 1
    else:
        stats["wrong_keys"] += 1

        dist = hamming_distance(key, EXPECTED_KEY)

        if dist == 1:
            stats["distance_histogram"]["1-bit"] += 1
        elif 2 <= dist <= 4:
            stats["distance_histogram"]["2-4-bit"] += 1
        elif 5 <= dist <= 8:
            stats["distance_histogram"]["5-8-bit"] += 1
        else:
            stats["distance_histogram"][">8-bit"] += 1

        sample_distance(key)

    if key == TROJAN_KEY:
        stats["trojan_keys"] += 1
        sample_trojan(key)

    last["key"] = key


def pct(name):
    return coverage_db[name].cover_percentage


def report_stats(log):
    log.info("===== KEY STATISTICS =====")
    log.info(f"Correct keys : {stats['correct_keys']}")
    log.info(f"Wrong keys   : {stats['wrong_keys']}")
    log.info(f"Trojan keys  : {stats['trojan_keys']}")

    log.info("Distance histogram:")
    for k, v in stats["distance_histogram"].items():
        log.info(f"  {k:>8}: {v}")