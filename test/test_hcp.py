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
    shcp = p1.find_shcp(course='orust', hcp=19.1, tee='yellow')
    assert(shcp==20)


def test_find_shcp_not_in_range():
    p1 = MyGit()
    shcp = p1.find_shcp(course='orust', hcp=54.1, tee='yellow')
    assert(shcp is None)


def test_brutto_hcp_calculation():
    p1 = MyGit()
    holes_par = p1.get_course_info('orust')['holes_par']
    shots = {i+1: holes_par[i]+1 for i in range(len(holes_par))}
    hcp = p1.calc_bruttoscore_hcp(course='orust', shots=shots, pcc=0)
    assert(hcp == 17.5)


def test_stableford_hcp_calculation():
    p1 = MyGit()
    hcp = p1.calc_stableford_hcp(course='orust', hcp=19.1, points=38, holes=18, pcc=0, tee='yellow')
    assert(hcp == 17.5)


def test_equal_hcp_calc():
    p1 = MyGit()

    holes_par = p1.get_course_info('orust')['holes_par']
    shots = {i+1: holes_par[i]+1 for i in range(len(holes_par))}
    
    h1 = p1.calc_bruttoscore_hcp(course='orust', shots=shots, pcc=0)
    h2 = p1.calc_stableford_hcp(course='orust', hcp=19.1, points=38, holes=18, pcc=0, tee='yellow')
    assert(h1 == h2)
