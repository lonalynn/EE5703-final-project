"""env/stimulus.py -- constrained-random keys and payloads for secure_gate (pyvsc)."""
import vsc

from env.gate_env import EXPECTED_KEY

RIGHT, OTHER = 0, 1 # classes of key: add yours

@vsc.randobj
class KeyTxn:
    """One key and one payload."""
    def __init__(self):
        self.kind = vsc.rand_uint8_t() # which class of key
        self.other = vsc.rand_bit_t(32) # the key, when the class is OTHER
        self.data = vsc.rand_bit_t(8)
        self.roll = vsc.rand_uint8_t()
        self.right_pct = vsc.uint8_t(30) # not rand: the test sets the mix
        
        @vsc.constraint
        def legal_c(self): # what each class means
            self.kind < 2
            self.other != EXPECTED_KEY # OTHER is always a wrong key

        @vsc.constraint
        def shape_c(self): # your choices
            self.roll < 100
            vsc.solve_order(self.roll, self.kind) # the roll first, so the weight holds

            with vsc.if_then(self.roll < self.right_pct):
                self.kind == RIGHT

            with vsc.else_then():
                self.kind == OTHER # a class of your own goes between these two

        def key(self):
            """The key the driver takes."""
            return EXPECTED_KEY if int(self.kind) == RIGHT else int(self.other)
