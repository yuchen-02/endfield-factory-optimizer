import json
import math
from scipy.optimize import linprog

with open("recipes.json", encoding="utf-8") as f:
    data = json.load(f)

#只留自動機器配方
auto_recipes = []

for r in data["recipes"]:
    if data["machines"][r["machine"]]["automated"]:
        print(r["id"], r["machine"])
        auto_recipes.append(r)
            
print(len(auto_recipes))

#算每台機器每秒的淨速率：產出為正、消耗為負
rates = []
for r in auto_recipes:
    rate = {}
    for name, amount in r["inputs"].items():
        rate[name] = rate.get(name, 0) - amount / r["time_sec"]
    for name, amount in r["outputs"].items():
        rate[name] = rate.get(name, 0) + amount / r["time_sec"]
    rates.append(rate)

for r, rate in zip(auto_recipes, rates):
    print(r["id"], rate)

#物品清單
items = sorted({item for rate in rates for item in rate})
#items = ['晶體外殼', '源礦']
matrix = [[rate.get(item, 0) for rate in rates] for item in items]
print(items)
print(matrix)

#目標物件
target_item = "晶體外殼"
target_per_sec = 30/60
demand = [target_per_sec if item == target_item else 0 for item in items]

#目標函數
cost = [data["machines"][r["machine"]]["power"]for r in auto_recipes]

#linprog只會看<= 我們要>=（產出>=需求），所以*-1可以反過來
A_ub = [[-v for v in row] for row in matrix] #ub = upper bound上界，不能超過，小於等於的效果
b_ub = [-d for d in demand]


result = linprog(c = cost, A_ub = A_ub, b_ub = b_ub, bounds = (0, None))

print("成功", result.success)
print("總耗電", result.fun)
for recipe, count in zip(auto_recipes, result.x):
    print(recipe["id"], recipe["machine"], "需要台數：", round(count, 4), "換算整數：", math.ceil(count - 1e-9))