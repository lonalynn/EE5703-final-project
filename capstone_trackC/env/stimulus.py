
import vsc

from env.gate_env import EXPECTED_KEY

RIGHT, CLOSE, OTHER = 0, 1, 2 # classes of key: add yours

@vsc.randobj
class KeyTxn:
    """One key and one payload."""
    def __init__(self):
        self.kind = vsc.rand_uint8_t() # which class of key
        self.other = vsc.rand_bit_t(32) # the key, when the class is OTHER
        self.close_bit = vsc.rand_uint8_t() # Additional bit flip when class is CLOSE
        self.data = vsc.rand_bit_t(8)
        self.roll = vsc.rand_uint8_t()
        self.right_pct = vsc.uint8_t(30) # not rand: the test sets the mix
        
    @vsc.constraint
    def legal_c(self): # what each class means
        self.kind < 3
        self.other != EXPECTED_KEY # OTHER is always a wrong key
        self.close_bit < 32   # Ensure a valid bit is selected

    @vsc.constraint
    def shape_c(self): # your choices
        self.roll < 100
        vsc.solve_order(self.roll, self.kind) # the roll first, so the weight holds

        with vsc.if_then(self.roll < self.right_pct):
            self.kind == RIGHT

        with vsc.else_if(self.roll < 60):
            self.kind == CLOSE

        with vsc.else_then():
            self.kind == OTHER # a class of your own goes between these two

    def key(self):
        """The key the driver takes."""
        if int(self.kind) == RIGHT:
            return EXPECTED_KEY
        elif int(self.kind) == CLOSE:
            return EXPECTED_KEY ^ (1 << int(self.close_bit))
        else:
            return int(self.other)
    
