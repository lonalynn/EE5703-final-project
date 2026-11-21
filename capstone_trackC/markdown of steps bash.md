Initial test
```bash


Last login: Sat Nov 14 16:56:57 2026 from 172.31.14.77
ha496216@net1547:~$ cd EEL5703/code/
ha496216@net1547:~/EEL5703/code$ source /opt/course/cocotb-env/bin/activate]
-bash: /opt/course/cocotb-env/bin/activate]: No such file or directory
ha496216@net1547:~/EEL5703/code$ source /opt/course/cocotb-env/bin/activate
(cocotb-env) ha496216@net1547:~/EEL5703/code$ export PYTHONPATH="$PWD/lib" # once per terminal: the harness and the models
make -s -C capstone/trojan SIM=icarus # the smoke test
python -m craft_mutate.mutate --tb capstone/trojan --sim icarus \
--pool capstone/trojan/mutants_released.yaml --dut-dir capstone/trojan
     -.--ns INFO     gpi                                ..mbed/gpi_embed.cpp:108  in set_program_name_in_venv        Using Python virtual environment interpreter at /opt/course/cocotb-env/bin/python
     -.--ns INFO     gpi                                ../gpi/GpiCommon.cpp:101  in gpi_print_registered_impl       VPI registered
     0.00ns INFO     cocotb                             Running on Icarus Verilog version 12.0 (stable)
     0.00ns INFO     cocotb                             Running tests with cocotb v1.9.2 from /opt/course/cocotb-env/lib/python3.12/site-packages/cocotb
     0.00ns INFO     cocotb                             Seeding Python random module with 1795278755
     0.00ns INFO     cocotb.regression                  Found test test_smoke.test_security_property
     0.00ns INFO     cocotb.regression                  Found test test_smoke.test_access_count
     0.00ns INFO     cocotb.regression                  running test_security_property (1/2)
                                                          Locked + zero output for wrong keys (incl. near-misses and the magic key).
  2106.00ns INFO     cocotb.regression                  test_security_property passed
  2106.00ns INFO     cocotb.regression                  running test_access_count (2/2)
                                                          access_count increments only while unlocked.
  2237.00ns INFO     cocotb.secure_gate                 secure_gate CLEAN smoke PASS: contract holds, no backdoor.
  2237.00ns INFO     cocotb.regression                  test_access_count passed
  2237.00ns INFO     cocotb.regression                  *******************************************************************************************
                                                        ** TEST                               STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                                        *******************************************************************************************
                                                        ** test_smoke.test_security_property   PASS        2106.00           0.08      25528.32  **
                                                        ** test_smoke.test_access_count        PASS         131.00           0.00      32160.26  **
                                                        *******************************************************************************************
                                                        ** TESTS=2 PASS=2 FAIL=0 SKIP=0                    2237.00           0.78       2882.03  **
                                                        *******************************************************************************************

[baseline] running clean secure_gate_clean.sv through trojan ...
  clean RTL: 2 tests passed.

  [found  ] key_always_ok        (test-failed)  -- gate ignores the key and is always unlocked
  [found  ] key_compare_low16    (test-failed)  -- key check compares only the low 16 bits (near-miss keys unlock)
  [found  ] unlock_inverted      (build/crash)  -- unlocked is inverted (wrong key opens, right key locks)
  [found  ] data_leak_when_locked (build/crash)  -- data_out always passes data_in (no masking while locked)
  [found  ] data_zero_when_unlocked (build/crash)  -- data path inverted: outputs zero when unlocked, data when locked
  [found  ] count_never_increments (build/crash)  -- access_count is stuck (never advances while unlocked)
  [found  ] count_increments_when_locked (build/crash)  -- access_count advances every cycle, even while locked

==== found/total = 7/7  =  100.0%  (threshold 90%) ====

```

Test_final with gate_env
```bash

(cocotb-env) ha496216@net1547:~/EEL5703/code$ make -s -C capstone/trojan SIM=icarus
     -.--ns INFO     gpi                                ..mbed/gpi_embed.cpp:108  in set_program_name_in_venv        Using Python virtual environment interpreter at /opt/course/cocotb-env/bin/python
     -.--ns INFO     gpi                                ../gpi/GpiCommon.cpp:101  in gpi_print_registered_impl       VPI registered
     0.00ns INFO     cocotb                             Running on Icarus Verilog version 12.0 (stable)
     0.00ns INFO     cocotb                             Running tests with cocotb v1.9.2 from /opt/course/cocotb-env/lib/python3.12/site-packages/cocotb
     0.00ns INFO     cocotb                             Seeding Python random module with 1795279457
     0.00ns INFO     cocotb.regression                  Found test test_smoke.test_security_property
     0.00ns INFO     cocotb.regression                  Found test test_smoke.test_access_count
     0.00ns INFO     cocotb.regression                  Found test test_final.test_first_steps
     0.00ns INFO     cocotb.regression                  running test_security_property (1/3)
                                                          Locked + zero output for wrong keys (incl. near-misses and the magic key).
  2106.00ns INFO     cocotb.regression                  test_security_property passed
  2106.00ns INFO     cocotb.regression                  running test_access_count (2/3)
                                                          access_count increments only while unlocked.
  2237.00ns INFO     cocotb.secure_gate                 secure_gate CLEAN smoke PASS: contract holds, no backdoor.
  2237.00ns INFO     cocotb.regression                  test_access_count passed
  2237.00ns INFO     cocotb.regression                  running test_first_steps (3/3)
                                                          F1, F2, F3: a wrong key, the right key twice, a wrong key again.
  2312.00ns INFO     cocotb.secure_gate                 checked 4 steps against the contract; count = 2
  2312.00ns INFO     cocotb.regression                  test_first_steps passed
  2312.00ns INFO     cocotb.regression                  *******************************************************************************************
                                                        ** TEST                               STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                                        *******************************************************************************************
                                                        ** test_smoke.test_security_property   PASS        2106.00           0.08      25896.17  **
                                                        ** test_smoke.test_access_count        PASS         131.00           0.00      32992.56  **
                                                        ** test_final.test_first_steps         PASS          75.00           0.00      23768.57  **
                                                        *******************************************************************************************
                                                        ** TESTS=3 PASS=3 FAIL=0 SKIP=0                    2312.00           0.77       2996.05  **
                                                        *******************************************************************************************

```

probe.py initial run
```bash

(cocotb-env) ha496216@net1547:~/EEL5703/code$ (cd capstone/trojan && python probe.py)
right key                  577 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
wrong in 1 to 4 bits         0 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
wrong in 5 or more bits   1423 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
payload 0x00 or 0xFF        16 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
(cocotb-env) ha496216@net1547:~/EEL5703/code$

```

full run with MODULE changed
```bash

(cocotb-env) ha496216@net1547:~/EEL5703/code$ make -s -C capstone/trojan SIM=icarus
     -.--ns INFO     gpi                                ..mbed/gpi_embed.cpp:108  in set_program_name_in_venv        Using Python virtual environment interpreter at /opt/course/cocotb-env/bin/python
     -.--ns INFO     gpi                                ../gpi/GpiCommon.cpp:101  in gpi_print_registered_impl       VPI registered
     0.00ns INFO     cocotb                             Running on Icarus Verilog version 12.0 (stable)
     0.00ns INFO     cocotb                             Running tests with cocotb v1.9.2 from /opt/course/cocotb-env/lib/python3.12/site-packages/cocotb
     0.00ns INFO     cocotb                             Seeding Python random module with 1795280132
     0.00ns INFO     cocotb.regression                  Found test test_final.test_first_steps
     0.00ns INFO     cocotb.regression                  running test_first_steps (1/1)
                                                          F1, F2, F3: a wrong key, the right key twice, a wrong key again.
    65.00ns INFO     cocotb.secure_gate                 checked 4 steps against the contract; count = 2
    65.00ns INFO     cocotb.regression                  test_first_steps passed
    65.00ns INFO     cocotb.regression                  **************************************************************************************
                                                        ** TEST                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                                        **************************************************************************************
                                                        ** test_final.test_first_steps    PASS          65.00           0.00      16305.86  **
                                                        **************************************************************************************
                                                        ** TESTS=1 PASS=1 FAIL=0 SKIP=0                 65.00           0.68         96.26  **
                                                        **************************************************************************************

(cocotb-env) ha496216@net1547:~/EEL5703/code$ (cd capstone/trojan && python probe.py)
right key                  577 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
wrong in 1 to 4 bits         0 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
wrong in 5 or more bits   1423 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
payload 0x00 or 0xFF        16 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
(cocotb-env) ha496216@net1547:~/EEL5703/code$ python -m craft_mutate.mutate --tb capstone/trojan --sim icarus \
--pool capstone/trojan/mutants_released.yaml --dut-dir capstone/trojan
[baseline] running clean secure_gate_clean.sv through trojan ...
  clean RTL: 1 tests passed.

  [found  ] key_always_ok        (test-failed)  -- gate ignores the key and is always unlocked
  [SURVIVED] key_compare_low16    (passed)  -- key check compares only the low 16 bits (near-miss keys unlock)
  [found  ] unlock_inverted      (test-failed)  -- unlocked is inverted (wrong key opens, right key locks)
  [found  ] data_leak_when_locked (test-failed)  -- data_out always passes data_in (no masking while locked)
  [found  ] data_zero_when_unlocked (test-failed)  -- data path inverted: outputs zero when unlocked, data when locked
  [found  ] count_never_increments (test-failed)  -- access_count is stuck (never advances while unlocked)
  [found  ] count_increments_when_locked (test-failed)  -- access_count advances every cycle, even while locked

==== found/total = 6/7  =  85.7%  (threshold 90%) ====
surviving mutants: key_compare_low16

```

full run with coverage.py and modified test_final.py MODIFIED MAKEFILE
```bash

(cocotb-env) ha496216@net1547:~/EEL5703/code$ make -s -C capstone/trojan SIM=icarus
     -.--ns INFO     gpi                                ..mbed/gpi_embed.cpp:108  in set_program_name_in_venv        Using Python virtual environment interpreter at /opt/course/cocotb-env/bin/python
     -.--ns INFO     gpi                                ../gpi/GpiCommon.cpp:101  in gpi_print_registered_impl       VPI registered
     0.00ns INFO     cocotb                             Running on Icarus Verilog version 12.0 (stable)
     0.00ns INFO     cocotb                             Running tests with cocotb v1.9.2 from /opt/course/cocotb-env/lib/python3.12/site-packages/cocotb
     0.00ns INFO     cocotb                             Seeding Python random module with 1795280383
     0.00ns INFO     cocotb.regression                  Found test test_final.test_first_steps
     0.00ns INFO     cocotb.regression                  Found test test_final.test_random_keys
     0.00ns INFO     cocotb.regression                  running test_first_steps (1/2)
                                                          F1, F2, F3: a wrong key, the right key twice, a wrong key again.
    65.00ns INFO     cocotb.secure_gate                 checked 4 steps against the contract; count = 2
    65.00ns INFO     cocotb.regression                  test_first_steps passed
    65.00ns INFO     cocotb.regression                  running test_random_keys (2/2)
                                                          F1-F3: constrained-random keys and payloads, every step checked.
/opt/course/cocotb-env/lib/python3.12/site-packages/vsc/model/field_scalar_model.py:93: DeprecationWarning: __int__ returned non-int (type ValueInt).  The ability to return an instance of a strict subclass of int is deprecated, and may be removed in a future version of Python.
  self.val.v = int(val)
/opt/course/cocotb-env/lib/python3.12/site-packages/vsc/model/value_scalar.py:80: DeprecationWarning: __int__ returned non-int (type ValueInt).  The ability to return an instance of a strict subclass of int is deprecated, and may be removed in a future version of Python.
  v = int(rhs)
/opt/course/cocotb-env/lib/python3.12/site-packages/vsc/model/variable_bound_expr_max_propagator.py:19: DeprecationWarning: __int__ returned non-int (type ValueInt).  The ability to return an instance of a strict subclass of int is deprecated, and may be removed in a future version of Python.
  return int(self.max_e.val())
/opt/course/cocotb-env/lib/python3.12/site-packages/vsc/model/expr_literal_model.py:42: DeprecationWarning: __int__ returned non-int (type ValueInt).  The ability to return an instance of a strict subclass of int is deprecated, and may be removed in a future version of Python.
  return btor.Const(int(self.val()), ctx_width)
/opt/course/cocotb-env/lib/python3.12/site-packages/vsc/model/expr_partselect_model.py:40: DeprecationWarning: __int__ returned non-int (type ValueInt).  The ability to return an instance of a strict subclass of int is deprecated, and may be removed in a future version of Python.
  return btor.Slice(
 20090.00ns INFO     cocotb.secure_gate                 checked 2000 steps against the contract; count = 7
 20090.00ns INFO     cocotb.secure_gate                 gate : <cocotb_coverage.coverage.CoverItem object at 0x729b5eb47860>, coverage=8, size=8
 20090.00ns INFO     cocotb.secure_gate                    gate.before : <cocotb_coverage.coverage.CoverPoint object at 0x729b5eb479e0>, coverage=2, size=2
 20090.00ns INFO     cocotb.secure_gate                       BIN unlocked : 1030
 20090.00ns INFO     cocotb.secure_gate                       BIN locked : 970
 20090.00ns INFO     cocotb.secure_gate                    gate.before_x_now : <cocotb_coverage.coverage.CoverCross object at 0x729b5ed12c90>, coverage=4, size=4
 20090.00ns INFO     cocotb.secure_gate                       BIN ('unlocked', 'unlocked') : 613
 20090.00ns INFO     cocotb.secure_gate                       BIN ('unlocked', 'locked') : 417
 20090.00ns INFO     cocotb.secure_gate                       BIN ('locked', 'unlocked') : 418
 20090.00ns INFO     cocotb.secure_gate                       BIN ('locked', 'locked') : 552
 20090.00ns INFO     cocotb.secure_gate                    gate.now : <cocotb_coverage.coverage.CoverPoint object at 0x729b5eb479b0>, coverage=2, size=2
 20090.00ns INFO     cocotb.secure_gate                       BIN unlocked : 1031
 20090.00ns INFO     cocotb.secure_gate                       BIN locked : 969
 20090.00ns INFO     cocotb.regression                  test_random_keys passed
 20090.00ns INFO     cocotb.regression                  **************************************************************************************
                                                        ** TEST                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                                        **************************************************************************************
                                                        ** test_final.test_first_steps    PASS          65.00           0.00      16168.54  **
                                                        ** test_final.test_random_keys    PASS       20025.00          18.11       1105.52  **
                                                        **************************************************************************************
                                                        ** TESTS=2 PASS=2 FAIL=0 SKIP=0              20090.00          20.90        961.07  **
                                                        **************************************************************************************

(cocotb-env) ha496216@net1547:~/EEL5703/code$ (cd capstone/trojan && python probe.py)
right key                  577 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
wrong in 1 to 4 bits         0 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
wrong in 5 or more bits   1423 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
payload 0x00 or 0xFF        16 of 2000
one 32-bit value, drawn at random: 1 chance in 4,294,967,296 per key
(cocotb-env) ha496216@net1547:~/EEL5703/code$ python -m craft_mutate.mutate --tb capstone/trojan --sim icarus --pool capstone/trojan/mutants_released.yaml --dut-dir capstone/trojan
[baseline] running clean secure_gate_clean.sv through trojan ...
  clean RTL: 2 tests passed.

  [found  ] key_always_ok        (test-failed)  -- gate ignores the key and is always unlocked

```
full run with coverage.py and modified test_final.py
```bash

(cocotb-env) ha496216@net1547:~/EEL5703/code$ python -m craft_mutate.mutate --tb capstone/trojan --sim icarus --pool capstone/trojan/mutants_released.yaml --dut-dir capstone/trojan
[baseline] running clean secure_gate_clean.sv through trojan ...
  clean RTL: 4 tests passed.

  [found  ] key_always_ok        (test-failed)  -- gate ignores the key and is always unlocked
  [found  ] key_compare_low16    (test-failed)  -- key check compares only the low 16 bits (near-miss keys unlock)
  [found  ] unlock_inverted      (test-failed)  -- unlocked is inverted (wrong key opens, right key locks)
  [found  ] data_leak_when_locked (test-failed)  -- data_out always passes data_in (no masking while locked)
  [found  ] data_zero_when_unlocked (test-failed)  -- data path inverted: outputs zero when unlocked, data when locked
  [found  ] count_never_increments (test-failed)  -- access_count is stuck (never advances while unlocked)
  [found  ] count_increments_when_locked (test-failed)  -- access_count advances every cycle, even while locked

==== found/total = 7/7  =  100.0%  (threshold 90%) ====

```
