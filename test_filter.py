from sites.filters import is_tcg_product

test_titles = [
    "Squishmallow: 10 Inch W4 Pokemon - Teddiursa",
    "Pokemon Mega Zygarde ex Premium Collection",
]

for t in test_titles:
    print(f"{t!r} -> is_tcg_product = {is_tcg_product(t)}")
