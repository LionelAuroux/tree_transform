import logging

log = logging.getLogger(__file__)

def simplifyNeg(node):
    log.info(f"simplifyNeg {node}")
    match node:
        case ["-", ["-", expr]]:
            res = expr
            log.info(f"{'>' * 10} simplifyNeg -- = {res}")
            return res
        case ["-", int() as expr]:
            res = -expr
            log.info(f"{'>' * 10} simplifyNeg - = {res}")
            return res
        case ["-", ["+", int() as expr]]:
            res = -expr
            log.info(f"{'>' * 10} simplifyNeg -+ = {res}")
            return res
        case ["+", ["-", int() as expr]]:
            res = -expr
            log.info(f"{'>' * 10} simplifyNeg +- = {res}")
            return res
        case _:
            return node

def castToInt(node):
    log.info(f"castToInt {repr(node)}")
    match node:
        case str() as expr:
            try:
                res = int(expr)
                log.info(f"{'>' * 10} castToInt = {res}")
                return res
            except ValueError:
                # unable to cast, so don't touch the variable
                return node
        case _:
            return node

def simplifyPlus(node):
    log.info(f"simplifyPlus {node}")
    match node:
        case ["+", int() as left, int() as right]:
            res = left + right
            log.info(f"{'>' * 10} simplifyPlus = {res}")
            return res
        case _:
            return node

def calc(node):
    log.info(f"Node {node}")
    ctx = {'a': 2600, 'b': 42}
    match node:
        case [expr]:
            res = calc(expr)
        case ["+", left, right]:
            res = calc(left) + calc(right)
        case ["-", left, right]:
            res = calc(left) - calc(right)
        case ["*", left, right]:
            res = calc(left) * calc(right)
        case ["/", left, right]:
            res = calc(left) / calc(right)
        case ["%", left, right]:
            res = calc(left) % calc(right)
        case ["-", expr]:
            res = - calc(expr)
        case ["+", expr]:
            res = calc(expr)
        case int() as expr:
            res = expr
        case str() as expr:
            res = ctx[expr]
        case _ as err:
            raise RuntimeError(f"Unknown {err}")
    log.info(f"partial {res}")
    return res

def apply(fn, node):
    from tree_transform import fixpoint, cache_node
    log.info(f"Apply {node}")
    match node:
        case (str() as a, b, c):
            b = fixpoint(apply, fn, b)
            c = fixpoint(apply, fn, c)
            return cache_node(a, b, c)
        case (str() as a, b):
            b = fixpoint(apply, fn, b)
            return cache_node(a, b)
        case _ as expr:
            return node

def test_base():
    from tree_transform import fixpoint, funcs
    ast = ["*", ["+", ["-", 4], "6"], ["-", ["+", ["/", 'b', 2], ["-", ["-", ['-', 'a', ['+', '1000', 1032]]]]]]]
    log.info("BAST: {ast}")
    ast = fixpoint(apply, funcs.runall(castToInt, simplifyPlus, simplifyNeg), ast)
    log.info(f"FINAL: {ast}")
    r = calc(ast)
    log.info(f"RES: {r}")
    assert type(r) == float
    assert r == -1178.0

def walk_list(fn, node):
    from tree_transform import fixpoint, cache_node
    log.info(f"Walk {node}")
    match node:
        case [*e]:
            log.info(f"Match [*e] {e}")
            lsid = []
            for n in e:
                lsid.append(fixpoint(walk_list, fn, n))
            log.info(f"RETWALK {lsid}")
            return cache_node(*lsid)
        case str() as expr:
            log.info(f"Match STR {expr}")
            return expr
    raise RuntimeError(f"Musn't go here {node}")

def test_sibling():
    def sibl(node):
        log.info(f"SIBL {node}")
        match node:
            case ["a", "b", *content]:
                log.info(f"HERE {'*'*10}: {content}")
                match content:
                    case [*other, "d", "e"]:
                        log.info(f"HI {'*'*10}: {other}")
                        return other
            case [uniq]:
                return uniq
        return node
    from tree_transform import fixpoint, funcs
    ast = ["a", "b", "c", "d", "e"]
    log.info(f"SIBLING: {ast}")
    ast = fixpoint(walk_list, funcs.runall(sibl), ast)
    log.info(f"FINAL: {ast}")
    assert ast == "c"

def test_match():
    p = [1, 2, 3, 4, 5, 6, 7, 8]
    res = False
    part = None
    while len(p):
        log.info(f"Check {p}")
        match p:
            case [4, 5, *right]:
                res = True
                part = right
                break
        p = p[1:]
    assert res
    assert part == [6, 7, 8]
