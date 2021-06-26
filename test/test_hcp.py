import sys
from pathlib import Path

cwd = Path.cwd()
sys.path.append(str(cwd.parent))
from hcp import MyGit


def test_basic():
    obj = MyGit()
    assert(obj is not None)


def test_find_shcp_in_range():
    p1 = MyGit()
    shcp = p1.find_shcp('orust', 19.1, tee='yellow')
    assert(shcp==20)


def test_find_shcp_not_in_range():
    p1 = MyGit()
    shcp = p1.find_shcp('orust', 54.1, tee='yellow')
    assert(shcp is None)


def test_brutto_hcp_calculation():
    p1 = MyGit()
    hcp = p1.calc_bruttoscore_hcp('orust', 92)
    assert(hcp == 19.3)


def test_stableford_hcp_calculation():
    p1 = MyGit()
    hcp = p1.calc_stableford_hcp('orust', 19.1, 36, tee='yellow')
    assert(hcp == 19.3)


def test_equal_hcp_calc():
    p1 = MyGit()
    h1 = p1.calc_stableford_hcp('orust', 19.1, 36, tee='yellow')
    h2 = p1.calc_bruttoscore_hcp('orust', 92)
    assert(h1 == h2)
