

class AppTestIntOp:
    spaceconfig = dict(usemodules=['__pypy__'])

    def w_intmask(self, n):
        import sys
        n &= (sys.maxint*2+1)
        if n > sys.maxint:
            n -= 2*(sys.maxint+1)
        return int(n)

    def test_intmask(self):
        import sys
        assert self.intmask(sys.maxint) == sys.maxint
        assert self.intmask(sys.maxint+1) == -sys.maxint-1
        assert self.intmask(-sys.maxint-2) == sys.maxint
        N = 2 ** 128
        assert self.intmask(N+sys.maxint) == sys.maxint
        assert self.intmask(N+sys.maxint+1) == -sys.maxint-1
        assert self.intmask(N-sys.maxint-2) == sys.maxint

    def test_int_add(self):
        import sys
        from __pypy__ import intop
        assert intop.int_add(40, 2) == 42
        assert intop.int_add(sys.maxint, 1) == -sys.maxint-1
        assert intop.int_add(-2, -sys.maxint) == sys.maxint

    def test_int_sub(self):
        import sys
        from __pypy__ import intop
        assert intop.int_sub(40, -2) == 42
        assert intop.int_sub(sys.maxint, -1) == -sys.maxint-1
        assert intop.int_sub(-2, sys.maxint) == sys.maxint

    def test_int_mul(self):
        import sys
        from __pypy__ import intop
        assert intop.int_mul(40, -2) == -80
        assert intop.int_mul(-sys.maxint, -sys.maxint) == (
            self.intmask(sys.maxint ** 2))
