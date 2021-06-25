import sys
from pathlib import Path
import pytest

cwd = Path.cwd()
sys.path.append(str(cwd.parent))
from hcp import Player

def test_find_shcp_in_range():
    p1 = Player(19)
    shcp = p1.find_shcp('orust', tee='yellow')
    assert(shcp==20)

def test_find_shcp_not_in_range():
    p1 = Player(54.1)
    shcp = p1.find_shcp('orust', tee='yellow')
    assert(shcp is None)