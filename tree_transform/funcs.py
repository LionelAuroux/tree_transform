import logging

log = logging.getLogger(__file__)

class runall:
    def __init__(self, *funcs):
        self.funcs = funcs

    def __call__(self, node):
        n = node
        for f in self.funcs:
            n = f(n)
            log.info(f"out {id(n)}")
        return n
