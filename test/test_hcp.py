import sys
from pathlib import Path
import pytest

cwd = Path.cwd()
sys.path.append(str(cwd.parent))
from hcp import MyGit


def test_basic():
    obj = MyGit(hcp=1)
    assert(obj.hcp==1)


def test_find_shcp_in_range():
    p1 = MyGit(19)
    shcp = p1.find_shcp('orust', tee='yellow')
    assert(shcp==20)


def test_find_shcp_not_in_range():
    p1 = MyGit(54.1)
    shcp = p1.find_shcp('orust', tee='yellow')
    assert(shcp is None)


def test_brutto_hcp_calculation():
    p1 = MyGit(19.1)
    hcp = p1.calc_bruttoscore_hcp('orust', 92)
    assert(hcp == 19.3)


def test_stableford_hcp_calculation():
    p1 = MyGit(19.1)
    hcp = p1.calc_stableford_hcp('orust', 36, tee='yellow')
    assert(hcp == 19.3)


def test_equal_hcp_calc():
    p1 = MyGit(19.1)
    h1 = p1.calc_stableford_hcp('orust', 36, tee='yellow')
    h2 = p1.calc_bruttoscore_hcp('orust', 92)
    assert(h1 == h2)
