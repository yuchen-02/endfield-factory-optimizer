import copy
from pathlib import Path

import pytest
from pytest import approx

from solver import load_data, solve

DATA = load_data(Path(__file__).parent.parent / "recipes.json")


def test_target_30_matches_hand_calculation():
    out = solve(DATA, "晶體外殼", 30)
    assert out["machines"]["mine_ore_electric"][0] == approx(1.5)
    assert out["machines"]["refine_crystal_shell"][0] == approx(1.0)
    assert out["machines"]["mine_ore_electric"][1] == 2      # 進位
    assert out["power"] == approx(12.5)


def test_target_60_is_perfect_ratio():
    out = solve(DATA, "晶體外殼", 60)
    assert out["machines"]["mine_ore_electric"][1] == 3
    assert out["machines"]["refine_crystal_shell"][1] == 2
    assert out["power"] == approx(25)


def test_target_zero_needs_no_machines():
    out = solve(DATA, "晶體外殼", 0)
    assert out["power"] == approx(0)
    assert all(whole == 0 for _, whole in out["machines"].values())


def test_unknown_item_raises():
    with pytest.raises(ValueError):
        solve(DATA, "不存在的東西", 30)


def test_missing_raw_material_raises():
    broken = copy.deepcopy(DATA)
    broken["recipes"] = [r for r in broken["recipes"]
                         if r["id"] != "mine_ore_electric"]   # 沒人產源礦
    with pytest.raises(ValueError):
        solve(broken, "晶體外殼", 30)