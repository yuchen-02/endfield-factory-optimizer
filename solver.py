import json

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

items = sorted({item for rate in rates for item in rate})
#items = ['晶體外殼', '源礦']
matrix = [[rate.get(item, 0) for rate in rates] for item in items]
print(items)
print(matrix)