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