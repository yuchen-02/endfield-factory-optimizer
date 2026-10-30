import json
import math
from scipy.optimize import linprog


def load_data(path="recipes.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def solve(data, target_item, target_per_min):
    """回傳 {'power': 總耗電, 'machines': {配方id: (小數台數, 進位台數)}}"""
    # 1. 只留自動化機器的配方
    auto_recipes = [r for r in data["recipes"]
                    if data["machines"][r["machine"]]["automated"]]

    # 2. 每個配方「每台每秒」的淨速率
    rates = []
    for r in auto_recipes:
        rate = {}
        for item, qty in r["inputs"].items():
            rate[item] = rate.get(item, 0) - qty / r["time_sec"]
        for item, qty in r["outputs"].items():
            rate[item] = rate.get(item, 0) + qty / r["time_sec"]
        rates.append(rate)

    # 3. 物品清單與矩陣
    items = sorted({item for rate in rates for item in rate})
    if target_item not in items:
        raise ValueError(f"沒有任何自動化配方涉及「{target_item}」")
    matrix = [[rate.get(item, 0) for rate in rates] for item in items]

    # 4. 需求、耗電
    demand = [target_per_min / 60 if item == target_item else 0 for item in items]
    cost = [data["machines"][r["machine"]]["power"] for r in auto_recipes]

    # 5. 求解（≥ 乘 -1 變成 ≤）
    A_ub = [[-v for v in row] for row in matrix]
    b_ub = [-d for d in demand]
    result = linprog(c=cost, A_ub=A_ub, b_ub=b_ub, bounds=(0, None))
    if not result.success:
        raise ValueError("無解：" + result.message)

    machines = {}
    for r, x in zip(auto_recipes, result.x):
        machines[r["id"]] = (x, math.ceil(x - 1e-9))
    return {"power": result.fun, "machines": machines}


if __name__ == "__main__":
    out = solve(load_data(), "晶體外殼", 30)
    print("總耗電(小數解):", out["power"])
    for rid, (frac, whole) in out["machines"].items():
        print(rid, "台數:", round(frac, 4), "→ 進位:", whole)